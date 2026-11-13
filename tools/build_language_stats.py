#!/usr/bin/env python3
"""Build a GitHub language-byte card with Python's standard library.

Scope: public repositories owned by the configured user, including forks and
the profile repository. Private, organization-owned, and contributed repositories
are excluded. Publish aggregate language bytes, not repository inventories.
This measures code composition, NOT proficiency; GitHub Linguist rules apply.

GITHUB_TOKEN is optional for public API rate limits. No personal access token is
required. Every API call and validation finishes before assets are overwritten.
"""

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

USERNAME = "sanyamjain0315"
ROOT = Path(__file__).resolve().parents[1]
API_ROOT = "https://api.github.com"
TIMEOUT_SECONDS = 30
PALETTE = (
    "#3572a5", "#e5a228", "#9864d9", "#d45e78", "#269e91", "#dc7946",
    "#5585d4", "#a77a36", "#b260b0", "#638b45", "#c75252", "#498fa4",
)
SCOPE = {
    "visibility": "public",
    "ownership": "owned by sanyamjain0315 (not organization or contributed repositories)",
    "includes_forks": True,
    "includes_profile_repository": True,
    "language_exclusions": [],
    "measure": "Sum of GitHub REST /repos/{owner}/{repo}/languages byte counts",
    "deduplicated": False,
    "interpretation": "Repository code composition, not proficiency; GitHub Linguist rules apply.",
    "repository_details_published": False,
}


class StatsError(Exception):
    """An actionable API or data-validation failure."""


def api_get(path, *, token=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": f"{USERNAME}-language-stats",
    }
    if token is None:
        token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"{API_ROOT}{path}", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        remaining = exc.headers.get("X-RateLimit-Remaining", "unknown")
        reset = exc.headers.get("X-RateLimit-Reset")
        reset_note = ""
        if reset and reset.isdigit():
            reset_note = f"; reset {dt.datetime.fromtimestamp(int(reset), dt.UTC).isoformat()}"
        # Public Actions logs must not reveal a private repository's URL or
        # GitHub's response body. Exception details can contain both.
        raise StatsError(
            f"GitHub HTTP {exc.code} while reading repository statistics "
            f"(rate-limit remaining: {remaining}{reset_note}). "
            "Check token expiry, repository selection, Contents read permission, "
            "and API limits; no assets have been written."
        ) from None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        raise StatsError("GitHub request or JSON decoding failed; no assets have been written.") from None


def owned_repositories():
    repositories = []
    seen = set()
    page = 1
    while True:
        options = {"per_page": 100, "page": page, "sort": "full_name", "direction": "asc"}
        options["type"] = "owner"
        endpoint = f"/users/{USERNAME}/repos"
        query = urllib.parse.urlencode(options)
        batch = api_get(f"{endpoint}?{query}")
        if not isinstance(batch, list):
            raise StatsError("GitHub repository response was not a list.")
        for repo in batch:
            if (
                not isinstance(repo, dict)
                or not isinstance(repo.get("full_name"), str)
                or repo.get("private") is not False
                or repo.get("owner", {}).get("login", "").lower() != USERNAME.lower()
                or not isinstance(repo.get("fork"), bool)
            ):
                raise StatsError("GitHub returned a malformed or out-of-scope repository.")
            if repo["full_name"] in seen:
                raise StatsError("Repository pagination returned a duplicate; rerun for a consistent snapshot.")
            seen.add(repo["full_name"])
            repositories.append(repo)
        print(f"Repository page {page}: {len(batch)} public owned repositories", flush=True)
        if len(batch) < 100:
            return repositories
        page += 1


def language_rows(totals):
    """Largest-remainder rounding makes displayed percentages sum to 100.00%."""
    ordered = sorted(totals.items(), key=lambda item: (-item[1], item[0].casefold(), item[0]))
    total_bytes = sum(totals.values())
    if not total_bytes:
        return []
    units = [count * 10000 // total_bytes for _, count in ordered]
    remainder_order = sorted(
        range(len(ordered)),
        key=lambda i: (-(ordered[i][1] * 10000 % total_bytes), i),
    )
    for index in remainder_order[:10000 - sum(units)]:
        units[index] += 1
    return [
        {"name": name, "bytes": count, "percentage": units[i] / 100}
        for i, (name, count) in enumerate(ordered)
    ]


def collect_stats():
    repositories = owned_repositories()
    totals = {}
    repositories_with_data = 0
    for index, repo in enumerate(repositories, start=1):
        name = repo["full_name"]
        languages = api_get(f"/repos/{urllib.parse.quote(name, safe='/')}/languages")
        if not isinstance(languages, dict) or any(
            not isinstance(language, str) or not language
            or type(count) is not int or count < 0
            for language, count in languages.items()
        ):
            raise StatsError("GitHub returned an invalid language-byte response; no assets have been written.")
        for language, count in languages.items():
            if count:
                totals[language] = totals.get(language, 0) + count
        repositories_with_data += any(languages.values())
        print(f"Languages processed: {index}/{len(repositories)}", flush=True)
    return {
        "schema_version": 2,
        "username": USERNAME,
        "retrieved_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "repository_count": len(repositories),
        "fork_count": sum(repo["fork"] for repo in repositories),
        "repositories_with_language_data": repositories_with_data,
        "scope": {
            **SCOPE,
            "coverage": "Public owned repositories",
        },
        "total_bytes": sum(totals.values()),
        "language_count": len(totals),
        "percentage_rounding": "Largest remainder, 0.01 percentage points; nonempty totals sum to 100.00%.",
        "languages": language_rows(totals),
    }


def color_for(name):
    # Stable colors across additions/removals and across Python hash seeds.
    return PALETTE[int.from_bytes(hashlib.sha256(name.encode()).digest()[:2], "big") % len(PALETTE)]


def render_svg(stats, mobile=False):
    languages = stats["languages"]
    columns = 1 if mobile else 2
    rows = math.ceil(len(languages) / columns)
    card_width = 420 if mobile else 840
    margin = 24 if mobile else 40
    panel_margin = 12 if mobile else 20
    bar_width = card_width - 2 * margin
    bar_y = 196 if mobile else 148
    first_label_y = 258 if mobile else 210
    height = (420 if mobile else 302) + max(rows, 1) * 42
    date = stats["retrieved_at_utc"].split("T")[0]
    scope_label = "Public repositories only"
    pieces = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{card_width}" height="{height}" viewBox="0 0 {card_width} {height}" role="img" aria-labelledby="title description">
  <title id="title">Repository languages · {USERNAME}</title>
  <desc id="description">Language byte percentages across {stats['repository_count']} owned repositories. Scope: {escape(scope_label)}. Includes accessible forks and the profile repository. All languages are shown in descending byte order. Code composition, not proficiency. Retrieved {escape(stats['retrieved_at_utc'])}. Percentages use largest-remainder rounding.</desc>
  <style>
    svg {{ --bg: #f6f8fc; --panel: #ffffff; --text: #17253d; --muted: #53627a; --border: #dce3ef; --track: #e7ecf5; }}
    @media (prefers-color-scheme: dark) {{
      svg {{ --bg: #0c1220; --panel: #141e30; --text: #edf3ff; --muted: #acbdd5; --border: #293852; --track: #24334c; }}
    }}
    text {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; fill: var(--text); }}
    .muted {{ fill: var(--muted); }}
    .label {{ font-size: 18px; }}
    .percent {{ font-size: 18px; font-weight: 650; font-variant-numeric: tabular-nums; }}
  </style>
  <rect x="1" y="1" width="{card_width - 2}" height="{height - 2}" rx="22" fill="var(--bg)" stroke="var(--border)"/>
  <rect x="{panel_margin}" y="{panel_margin}" width="{card_width - 2 * panel_margin}" height="{height - 2 * panel_margin}" rx="16" fill="var(--panel)"/>''']
    if mobile:
        pieces.append(f'''<text x="24" y="54" font-size="20" font-weight="750">Repository languages</text>
  <text x="24" y="84" font-size="18" class="muted">@{USERNAME}</text>
  <text x="24" y="112" font-size="18" class="muted">{escape(scope_label)}</text>
  <text x="24" y="144" font-size="18" class="muted">{stats['repository_count']} repositories · {len(languages)} languages</text>
  <text x="24" y="172" font-size="18" class="muted">{stats['total_bytes']:,} code bytes</text>''')
    else:
        pieces.append(f'''<text x="40" y="62" font-size="28" font-weight="750">Repository languages</text>
  <text x="40" y="92" font-size="18" class="muted">@{USERNAME} · {escape(scope_label)}</text>
  <text x="40" y="123" font-size="17" class="muted">{stats['repository_count']} repositories · {len(languages)} languages · {stats['total_bytes']:,} code bytes</text>''')
    pieces.append(f'''<defs><clipPath id="bar"><rect x="{margin}" y="{bar_y}" width="{bar_width}" height="22" rx="11"/></clipPath></defs>
  <rect x="{margin}" y="{bar_y}" width="{bar_width}" height="22" rx="11" fill="var(--track)"/>
  <g clip-path="url(#bar)">''')
    offset = 0
    for language in languages:
        width = language["bytes"] / stats["total_bytes"] * bar_width
        pieces.append(
            f'<rect x="{margin + offset:.6f}" y="{bar_y}" width="{width:.6f}" height="22" fill="{color_for(language["name"])}">'
            f'<title>{escape(language["name"])}: {language["percentage"]:.2f}% ({language["bytes"]:,} bytes)</title></rect>'
        )
        offset += width
    pieces.append('</g>')
    for index, language in enumerate(languages):
        x = margin + (index % columns) * 396
        y = first_label_y + (index // columns) * 42
        # Fit unusually long names without dropping any language from the card.
        name_width = 250
        fit = f' textLength="{name_width}" lengthAdjust="spacingAndGlyphs"' if len(language["name"]) > 25 else ""
        pieces.append(
            f'<circle cx="{x + 6}" cy="{y - 6}" r="6" fill="{color_for(language["name"])}"/>'
            f'<text x="{x + 23}" y="{y}" class="label"{fit}>{escape(language["name"])}</text>'
            f'<text x="{x + (bar_width if mobile else 364)}" y="{y}" text-anchor="end" class="percent">{language["percentage"]:.2f}%</text>'
        )
    if not languages:
        pieces.append(f'<text x="{margin}" y="{first_label_y}" class="label muted">No language bytes reported by GitHub.</text>')
    percentage_total = '100.00' if languages else '0.00'
    if mobile:
        footer = height - 164
        footer_lines = [
            'Includes forks + profile repository.',
            'No language exclusions or deduplication.',
            'GitHub code bytes, not proficiency.',
            'Duplicated fork code counts.',
            f'Retrieved {date} UTC',
            f'Rounded percentages total {percentage_total}%.',
        ]
        pieces.append(f'<path d="M24 {footer - 22} H396" stroke="var(--border)"/>')
        for index, line in enumerate(footer_lines):
            pieces.append(f'<text x="24" y="{footer + 3 + index * 26}" font-size="18" class="muted">{escape(line)}</text>')
    else:
        footer = height - 97
        pieces.append(f'''<path d="M40 {footer - 22} H800" stroke="var(--border)"/>
  <text x="40" y="{footer + 3}" font-size="16" class="muted">Includes all forks + profile repository; no language exclusions.</text>
  <text x="40" y="{footer + 29}" font-size="16" class="muted">GitHub language bytes, not proficiency. Duplicated fork code counts.</text>
  <text x="40" y="{footer + 55}" font-size="16" class="muted">Retrieved {date} UTC · Percentages total {percentage_total}%</text>''')
    pieces.append('</svg>\n')
    return '\n'.join(pieces)


def validate_outputs(stats, *svgs):
    languages = stats["languages"]
    if stats["scope"].get("visibility") != "public":
        raise StatsError("Only public-repository statistics may be published.")
    if sum(row["bytes"] for row in languages) != stats["total_bytes"]:
        raise StatsError("Language bytes do not match the total.")
    if "repositories" in stats or stats["scope"].get("repository_details_published") is not False:
        raise StatsError("Public output must not contain a repository inventory.")
    if languages and sum(round(row["percentage"] * 100) for row in languages) != 10000:
        raise StatsError("Rounded percentages do not sum to 100.00%.")
    if languages != sorted(languages, key=lambda row: (-row["bytes"], row["name"].casefold(), row["name"])):
        raise StatsError("Languages are not sorted by byte count.")
    ns = {"s": "http://www.w3.org/2000/svg"}
    for svg in svgs:
        root = ET.fromstring(svg)
        labels = root.findall('.//s:text[@class="label"]', ns)
        percentages = root.findall('.//s:text[@class="percent"]', ns)
        if [label.text for label in labels] != [row["name"] for row in languages]:
            raise StatsError("SVG language labels do not match the data.")
        if [label.text for label in percentages] != [f"{row['percentage']:.2f}%" for row in languages]:
            raise StatsError("SVG percentages do not match the data.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    try:
        stats = collect_stats()
        svg = render_svg(stats)
        mobile_svg = render_svg(stats, mobile=True)
        validate_outputs(stats, svg, mobile_svg)
        json_text = json.dumps(stats, indent=2, ensure_ascii=False) + "\n"
        # No network calls beyond this point: API failures leave ALL old assets intact.
        (ROOT / "assets" / "languages.json").write_text(json_text, encoding="utf-8")
        (ROOT / "assets" / "languages.svg").write_text(svg, encoding="utf-8")
        (ROOT / "assets" / "languages-mobile.svg").write_text(mobile_svg, encoding="utf-8")
    except (StatsError, OSError, ET.ParseError) as exc:
        print(f"Language stats failed: {exc}", file=sys.stderr)
        return 1
    print(
        f"Generated assets: {stats['repository_count']} repositories "
        f"({stats['fork_count']} forks), {stats['language_count']} languages, "
        f"{stats['total_bytes']:,} bytes; retrieved {stats['retrieved_at_utc']}.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
