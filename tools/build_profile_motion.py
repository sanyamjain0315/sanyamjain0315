#!/usr/bin/env python3
"""Build self-contained README headings and responsive summary SVGs (stdlib only).

Run from any directory: python3 tools/build_profile_motion.py
Validate committed assets without writing: add --check.

Heading SMIL adapts WaterTian's MIT-licensed cookbook patterns 03 and 06:
https://github.com/WaterTian/svg-motion-cookbook/blob/c6e80da87bfcca69653fec66e1365f23f0e7e215/examples/03-clip-reveal-text.svg
https://github.com/WaterTian/svg-motion-cookbook/blob/c6e80da87bfcca69653fec66e1365f23f0e7e215/examples/06-color-shimmer.svg
The full upstream license is in THIRD_PARTY_NOTICES.md. Unlike the examples,
these accents run once, finish in 2.8 seconds, and never animate heading text.
Reduced motion hides the SMIL group; animation:none alone cannot stop SMIL.

Summary motion is an original diffusion-inspired approximation of parallel word
refinement, NOT an exact reproduction of Inception's live chat (research there
received HTTP 429). It uses independently shuffled word fades/blur and one low-
contrast, pre-authored nonsense overlay. No model, script, network, external font,
or browser-side randomness is used. CSS motion is opt-in, finite, and separate
from the default static duplicate. Every word settles within 2.5 seconds.

README integration (owned by the caller): heading images have height 40 and the
intrinsic widths printed below; give their h2 wrappers explicit stable anchors.
Use summary-mobile.svg for picture media="(max-width: 600px)", summary.svg as
its fallback, and provide the complete prose in alt text and native details.
Leave the shared summary img width unset: do not force width="100%" or a fixed
width. Intrinsic widths are 420px mobile and 700px desktop; GitHub's max-width:
100% constrains either to its container without stretching. Text is 18px at
intrinsic size, or approximately 15.5px if desktop scales to a 601px container.

This generator writes only assets/heading-*.svg and assets/summary*.svg. It does
not touch README, SETUP, preview, other assets, or the still image. To extract
that separately, Pillow is permitted only for the existing GIF's static frame:
  uv run --with Pillow python -c 'from PIL import Image; im = Image.open("assets/windows7.gif"); im.seek(0); im.convert("RGBA").save("assets/windows7-still.png")'
"""

import argparse
import hashlib
import random
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = "https://github.com/WaterTian/svg-motion-cookbook/blob/c6e80da87bfcca69653fec66e1365f23f0e7e215/examples/"
HEADINGS = (
    ("summary", "Summary", 420),
    ("showcase", "Showcase projects", 440),
    ("languages", "Languages across my GitHub", 480),
    ("skills", "Skills and tools I use", 460),
    ("ongoing", "Ongoing projects", 440),
    ("planned", "Planned projects", 440),
    ("interests", "Personal interests", 440),
)
PARAGRAPHS = (
    "I’m Sanyam, an M.S. Computer Science candidate at Boston University. I build event-driven backends and experiment with local AI agents. I’m happiest working out how a system behaves as events arrive, queues fill, and models make decisions.",
    "I believe AI should be open-source, private, and under its users’ control. That keeps me tinkering with local models—and learning something new about backend engineering every day.",
)
FONT_SIZE = 18
SUMMARY_WIDTHS = {"summary.svg": 700, "summary-mobile.svg": 420}
LINE_HEIGHT = 29
PADDING = 8
PARAGRAPH_GAP = 17
SVG_NS = "http://www.w3.org/2000/svg"

THEME_CSS = """
    text { fill: #253342; font-family: Arial, Helvetica, sans-serif; }
    .accent { stroke: #9a671f; }
    .theme-dark { display: none; }
    @media (prefers-color-scheme: dark) {
      text { fill: #e6edf3; }
      .accent { stroke: #d7b775; }
      .theme-light { display: none; }
      .theme-dark { display: inline; }
    }
"""


def advance(text):
    """Conservative proportional advances, in em; no installed font dependency.

    Explicit textLength keeps each rendered word inside its allocated advance,
    even when the host substitutes a local sans-serif. Slightly generous widths
    leave breathing room at 18px, rather than shrinking text to force a fit.
    """
    narrow = "ijlI.,:;!'’|"
    wide = "mwMW@%"
    return sum(
        0.29 if c in narrow else 0.88 if c in wide else
        0.30 if c == " " else 1.0 if c == "—" else
        0.67 if c.isupper() else 0.55
        for c in text
    ) * FONT_SIZE


def heading_svg(slug, title, width):
    underline = min(width - 20, round(advance(title) * 25 / FONT_SIZE))
    motion = []
    for theme, colors in (
        ("light", "#9a671f;#bc8a43;#9a671f"),
        ("dark", "#d7b775;#f0d5a0;#d7b775"),
    ):
        motion.append(f'''    <path class="theme-{theme}" d="M2 35 H{underline}" stroke="{colors.split(';')[0]}" stroke-width="2.5" stroke-linecap="round">
      <animate attributeName="stroke" values="{colors}" keyTimes="0;0.5;1" begin="0s" dur="2.8s" repeatCount="1" fill="freeze"/>
    </path>''')
    return f'''<svg xmlns="{SVG_NS}" width="{width}" height="40" viewBox="0 0 {width} 40" font-family="Arial, Helvetica, sans-serif" role="img" aria-labelledby="title desc">
  <!-- Generated by tools/build_profile_motion.py. Adapted from MIT-licensed patterns 03 and 06:
       {SOURCE}03-clip-reveal-text.svg
       {SOURCE}06-color-shimmer.svg
       Copyright (c) 2026 Water (WaterTian). Full license: ../THIRD_PARTY_NOTICES.md -->
  <title id="title">{escape(title)}</title>
  <desc id="desc">Stationary section heading; a single underline reveal and soft color shimmer finish in 2.8 seconds.</desc>
  <style>
{THEME_CSS}
    .heading-motion {{ display: none; }}
    @media (prefers-reduced-motion: no-preference) {{
      .heading-motion {{ display: inline; }}
      .static-accent {{ opacity: .28; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .heading-motion {{ display: none; }}
      .static-accent {{ opacity: 1; }}
    }}
  </style>
  <text x="2" y="26" fill="#253342" font-size="25" font-weight="600">{escape(title)}</text>
  <path class="accent static-accent" d="M2 35 H{underline}" stroke="#9a671f" stroke-width="2.5" stroke-linecap="round"/>
  <g class="heading-motion" display="none" fill="none" aria-hidden="true">
    <defs>
      <clipPath id="underline-reveal" clipPathUnits="userSpaceOnUse">
        <!-- Full-width base is readable if SMIL is unavailable. -->
        <rect x="0" y="32" width="{width}" height="7">
          <animate attributeName="width" values="0;{width};{width}" keyTimes="0;0.68;1" begin="0s" dur="1.8s" repeatCount="1" fill="freeze" calcMode="spline" keySplines="0.22 0.61 0.36 1;0 0 1 1"/>
        </rect>
      </clipPath>
    </defs>
    <g clip-path="url(#underline-reveal)">
{chr(10).join(motion)}
    </g>
  </g>
</svg>
'''


def layout_summary(width):
    """Greedy word wrapping with explicit, testable in-bounds word boxes."""
    words = []
    x, y = PADDING, 25
    right = width - PADDING
    for paragraph_index, paragraph in enumerate(PARAGRAPHS):
        for word in paragraph.split(" "):
            length = round(advance(word), 2)
            if x + length > right and x != PADDING:
                x, y = PADDING, y + LINE_HEIGHT
            if x + length > right:
                raise ValueError(f"Word too wide for {width}px summary: {word}")
            words.append((paragraph_index, word, round(x, 2), y, length))
            x += length + advance(" ")
        if paragraph_index + 1 < len(PARAGRAPHS):
            x, y = PADDING, y + LINE_HEIGHT + PARAGRAPH_GAP
    return words, y + 12


def word_element(word, x, y, length, attributes=""):
    return (f'      <text x="{x}" y="{y}" textLength="{length}" '
            f'lengthAdjust="spacingAndGlyphs"{attributes}>{escape(word)}</text>')


def summary_svg(width):
    words, height = layout_summary(width)
    # Same token gets the same timing in both layouts; never a left-right sweep.
    rng = random.Random(20261113)
    order = list(range(len(words)))
    rng.shuffle(order)
    ranks = {index: rank for rank, index in enumerate(order)}
    static, animated, noise = [], [], []
    for index, (_, word, x, y, length) in enumerate(words):
        delay = 0.08 + ranks[index] / len(words) * 1.0
        duration = 0.85 + rng.random() * 0.50
        static.append(word_element(word, x, y, length))
        animated.append(word_element(
            word, x, y, length,
            f' class="word" style="animation-delay:{delay:.3f}s;animation-duration:{duration:.3f}s"',
        ))
        # Sparse, pre-authored low-contrast noise: one burst, not flashing tokens.
        if index % 3 == 0:
            nonsense = "".join(rng.choice("aeinorstuvx") if c.isalpha() else c for c in word)
            noise.append(word_element(nonsense, x, y, length))
    return f'''<svg xmlns="{SVG_NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="Arial, Helvetica, sans-serif" font-size="{FONT_SIZE}" role="img" aria-labelledby="title desc">
  <!-- Generated by tools/build_profile_motion.py. Original diffusion-inspired parallel
       word refinement; not an exact reproduction of Inception live chat. No external resources. -->
  <title id="title">Summary</title>
  <desc id="desc">{escape(PARAGRAPHS[0])}\n\n{escape(PARAGRAPHS[1])}</desc>
  <style>
{THEME_CSS}
    text {{ font-size: {FONT_SIZE}px; }}
    .summary-static {{ display: inline; }}
    .summary-motion {{ display: none; }}
    .word {{ opacity: 1; filter: none; }}
    .noise {{ opacity: 0; }}
    /* No media-query or CSS animation/filter support means fully static prose. */
    @media (prefers-reduced-motion: no-preference) {{
      @supports (animation-name: word-resolve) and (filter: blur(1px)) {{
        .summary-static {{ display: none; }}
        .summary-motion {{ display: inline; }}
        .word {{ animation: word-resolve 1.1s cubic-bezier(.2,.65,.3,1) 1 both; }}
        .noise {{ animation: noise-dissolve 1.15s ease-out 1 both; }}
      }}
    }}
    /* Hide animated groups, including on a live preference change. */
    @media (prefers-reduced-motion: reduce) {{
      .summary-static {{ display: inline; }}
      .summary-motion {{ display: none; }}
    }}
    @keyframes word-resolve {{
      from {{ opacity: .12; filter: blur(2.6px); }}
      to {{ opacity: 1; filter: blur(0); }}
    }}
    @keyframes noise-dissolve {{
      0% {{ opacity: 0; }}
      18% {{ opacity: .22; }}
      100% {{ opacity: 0; }}
    }}
  </style>
  <g class="summary-static" fill="#253342" aria-hidden="true">
{chr(10).join(static)}
  </g>
  <g class="summary-motion" display="none" fill="#253342" aria-hidden="true">
    <g class="noise" opacity="0">
{chr(10).join(noise)}
    </g>
    <g class="resolved-words">
{chr(10).join(animated)}
    </g>
  </g>
</svg>
'''


def validate_svg(name, svg):
    """Check XML, resource isolation, layout, finite timelines and prose fidelity."""
    root = ET.fromstring(svg)
    ns = {"s": SVG_NS}
    if root.tag != f"{{{SVG_NS}}}svg":
        raise ValueError(f"{name}: not an SVG")
    ids = [node.get("id") for node in root.iter() if node.get("id")]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{name}: duplicate IDs")
    for node in root.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        if tag in {"script", "foreignObject", "image", "a", "use"}:
            raise ValueError(f"{name}: forbidden resource/active element {tag}")
        for key, value in node.attrib.items():
            if key.rsplit("}", 1)[-1].lower().startswith("on") or "href" in key:
                raise ValueError(f"{name}: external reference or event handler")
            for reference in re.findall(r"url\(([^)]+)\)", value):
                if not reference.startswith("#") or reference[1:] not in ids:
                    raise ValueError(f"{name}: non-local/broken resource reference")
        if tag == "animate":
            end = float(node.get("begin", "0s").removesuffix("s")) + float(node.attrib["dur"].removesuffix("s"))
            if node.get("repeatCount") != "1" or end >= 4 or node.get("fill") != "freeze":
                raise ValueError(f"{name}: animation must stop before four seconds")
    style = root.find("s:style", ns)
    if style is None or style.text is None:
        raise ValueError(f"{name}: missing fallback and motion CSS")
    css = style.text
    if re.search(r"@import|url\s*\(|infinite", css, re.IGNORECASE):
        raise ValueError(f"{name}: external CSS resource or endless animation")
    if "prefers-reduced-motion: no-preference" not in css or "prefers-reduced-motion: reduce" not in css:
        raise ValueError(f"{name}: explicit motion opt-in and reduced-motion fallback required")
    width, height = int(root.attrib["width"]), int(root.attrib["height"])
    if root.attrib["viewBox"] != f"0 0 {width} {height}":
        raise ValueError(f"{name}: intrinsic size/viewBox mismatch")
    if name.startswith("heading-"):
        if len(root.findall("s:text", ns)) != 1 or height != 40:
            raise ValueError(f"{name}: heading must have one stationary text node")
        motion = root.find("s:g[@class='heading-motion']", ns)
        if motion is None or motion.get("display") != "none":
            raise ValueError(f"{name}: SMIL group must be hidden by default")
        if ".heading-motion { display: none; }" not in css:
            raise ValueError(f"{name}: reduced motion must hide SMIL, not just CSS animation")
    else:
        expected_width = SUMMARY_WIDTHS[name]
        expected_height = layout_summary(expected_width)[1]
        if (width, height) != (expected_width, expected_height):
            raise ValueError(f"{name}: expected intrinsic size {expected_width}×{expected_height}")
        if root.get("font-size") != str(FONT_SIZE):
            raise ValueError(f"{name}: summary must retain {FONT_SIZE}px text")
        description = root.find("s:desc", ns)
        if description is None or description.text != "\n\n".join(PARAGRAPHS):
            raise ValueError(f"{name}: summary prose changed")
        static = root.find("s:g[@class='summary-static']", ns)
        if static is None:
            raise ValueError(f"{name}: missing static summary fallback")
        words = static.findall("s:text", ns)
        if " ".join(node.text or "" for node in words) != " ".join(PARAGRAPHS):
            raise ValueError(f"{name}: rendered prose differs from original")
        for node in words:
            x, y, length = (float(node.attrib[k]) for k in ("x", "y", "textLength"))
            if x < PADDING or x + length > width - PADDING or not FONT_SIZE <= y <= height - 8:
                raise ValueError(f"{name}: out-of-bounds word {node.text}")
        timings = []
        for node in root.findall(".//s:text[@class='word']", ns):
            delay, duration = map(float, re.findall(r":([0-9.]+)s", node.attrib["style"]))
            timings.append(delay + duration)
        if len(timings) != len(words) or max(timings) >= 2.5:
            raise ValueError(f"{name}: word refinement did not settle before 2.5 seconds")
    return width, height


def build_assets():
    assets = {f"heading-{slug}.svg": heading_svg(slug, title, width) for slug, title, width in HEADINGS}
    assets.update((name, summary_svg(width)) for name, width in SUMMARY_WIDTHS.items())
    return assets


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="validate existing output and deterministic regeneration without writing")
    args = parser.parse_args()
    assets = build_assets()
    # Validate everything before touching any output file.
    dimensions = {name: validate_svg(name, content) for name, content in assets.items()}
    if args.check:
        for name, expected in assets.items():
            actual = (ASSETS / name).read_text(encoding="utf-8")
            validate_svg(name, actual)
            if actual != expected:
                raise ValueError(f"assets/{name} is stale; run {Path(__file__).name}")
    else:
        for name, content in assets.items():
            (ASSETS / name).write_text(content, encoding="utf-8")
    for name, content in assets.items():
        width, height = dimensions[name]
        digest = hashlib.sha256(content.encode()).hexdigest()[:12]
        print(f"{'Checked' if args.check else 'Built'} assets/{name}: {width}×{height}, sha256 {digest}")
    print("Validated 9 SVGs: XML, exact prose, bounds, local-only resources, finite timing, static/reduced-motion structure.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, ET.ParseError) as exc:
        sys.exit(f"Profile motion build failed: {exc}")
