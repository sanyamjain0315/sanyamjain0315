# Publish the GitHub profile

The profile uses `README.md`, `assets/`, and `windows-xp-profile.html` in the public
[`sanyamjain0315/sanyamjain0315`](https://github.com/sanyamjain0315/sanyamjain0315)
repository. Keep the relative asset paths intact. No changes have been published
by the local editing tools.

## 1. Enable the clickable desktop

The README starts with the supplied `assets/windows7.gif`. Clicking it opens:

<https://sanyamjain0315.github.io/sanyamjain0315/windows-xp-profile.html>

GitHub normally shows an HTML file's **source**, not an interactive website. To
serve the desktop itself:

1. Publish the HTML and its referenced image assets to `main`.
2. Open the repository's **Settings → Pages**.
3. Select **Deploy from a branch**, **main**, and **/ (root)**; save.
4. Wait for the Pages deployment, then test the URL above.

Pages was disabled when this profile was prepared, so the banner link will not
work until that one-time setting is enabled. If you use another host, replace
the first link in `README.md`. The local desktop can be opened directly from
`windows-xp-profile.html` without Pages.

The GIF is unchanged. Readers who prefer reduced motion receive
`assets/windows7-still.png`, its first frame, through a `<picture>` source.

## 2. Language percentages — no external service required

`assets/languages.svg` and the single-column `assets/languages-mobile.svg` are
checked-in snapshots generated from GitHub's REST API. They are visible
immediately, even before automation is enabled. The mobile layout is selected
below 600px and keeps an intrinsic width of 420px instead of stretching.

- Scope: **public repositories owned by `sanyamjain0315`**, including forks,
  archived repositories, and this profile. Private, organization-owned, and
  contributed repositories are excluded. New public repositories are discovered
  automatically on each refresh using GitHub's public-user repository endpoint.
- **HTML and Jupyter Notebook are excluded** from the chart and its percentage
  denominator. Their bytes are not reassigned to another language. The remaining
  languages are normalized to total **100.00%**, unless none remain.
- The percentages sum **included language bytes**, not repository counts,
  commits, proficiency, or time spent. Repeated fork code can influence the
  result. A tiny included language can round to `0.00%` without being excluded.
  `repositories_with_language_data` counts repositories with at least one
  nonzero included language.
- `assets/languages.json` publishes **aggregate language bytes and percentages**,
  aggregate counts, scope, and retrieval time. Repository names, URLs, visibility
  breakdowns, and per-repository language totals are never published. Progress
  logs and API error messages also omit repository identifiers. Private data is
  not requested or included.

### Automatic weekly refresh

Publish `.github/workflows/language-stats.yml` and
`tools/build_language_stats.py` along with the assets. Enable **GitHub Actions**
for the repository. The workflow runs on Mondays at **06:17 UTC**, and can also
be run manually from **Actions → Refresh repository languages → Run
workflow**. Scheduled runs can be delayed by GitHub.

The workflow uses the automatic `GITHUB_TOKEN` for public API rate limits and
saving the three generated assets to `main`. No personal access token or custom
secret is needed. The former `LANGUAGE_STATS_TOKEN` secret is no longer read;
you can remove it from this repository's Actions secrets. If the associated PAT
was created only for this workflow, you can also revoke it in account settings.

Repository policies must allow the workflow token to push generated assets to
`main`; branch protection may require a local update and PR instead. No external
stats service or paid account is required. API failures leave existing assets
intact. The workflow does not require a separately committed test script.

To refresh public data locally with Python 3.11+ (optional `GITHUB_TOKEN` raises
API limits):

```sh
python3 tools/build_language_stats.py
```

Select **Actions → Refresh repository languages → Run workflow** after
publishing these changes to refresh immediately rather than waiting for Monday.
Private-repository collection and the `--include-private` option have been
removed; even an authenticated run uses the public-only endpoint.

There is no browser-side API call or visitor tracking. These are snapshots, not
real-time stats; README images may additionally be cached by GitHub. Automatic
refresh updates the **GitHub README**. Commits made with `GITHUB_TOKEN` do not
trigger branch-based Pages builds, so a Pages-hosted copy of `preview.html` can
retain older stats until the next Pages deployment; the desktop banner link is
unaffected.

## 3. Headings and diffusion-inspired summary

The section headings adapt the clip reveal and color shimmer patterns from
[WaterTian's SVG motion cookbook](https://github.com/WaterTian/svg-motion-cookbook).
Their text stays stationary while an underline reveals and shimmers once. All
motion ends within 2.8 seconds. Attribution and the upstream MIT license are in
`THIRD_PARTY_NOTICES.md`.

The summary resolves words in parallel from faint, blurred text and a brief
scrambled overlay, rather than typing left to right. It is an SVG approximation
inspired by diffusion text generation, **not Inception's actual chat renderer**.
The live chat could not be inspected because it returned a security checkpoint.
GitHub README content cannot run that site's JavaScript or embed its chat UI.
No Inception API, credentials, model calls, or external fonts are used.

The summary has intrinsic-width desktop (700px) and mobile (420px) layouts,
light/dark colors, full alt text,
and an expandable selectable-text version. Static SVG groups are shown for
reduced motion or when animation support is unavailable. Reduced motion hides
SMIL groups rather than incorrectly relying on `animation: none` to stop them.
Heading and summary animation is finite and does not loop.

Clicking the summary in the GitHub README opens `summary.html`, where clicking
it (or pressing Enter/Space on its button) restarts the animation. Publish this
page and `assets/summary-replay.js` with the other Pages files. The README itself
cannot run JavaScript or restart an SVG image on click; the linked page is the
interactive fallback. The local `preview.html` supports in-place click replay
using the same script. Replay respects reduced motion and leaves the summary
static when that preference is enabled. With JavaScript disabled, reloading the
replay page is the fallback.

To edit the summary or heading labels, update `tools/build_profile_motion.py`,
then run:

```sh
python3 tools/build_profile_motion.py
python3 tools/build_profile_motion.py --check
```

The supplied desktop GIF is independent of these effects; regenerate it
separately if you change the HTML and want the recording to match.

## 4. Content and preview

The README order is banner, summary, showcase projects, language percentages,
skills/tools, ongoing projects, planned projects, and personal interests.
NoDust and the CUDA project are the primary showcase. YT Gatekeeper is retained
in an expandable entry. BU Spark! and the phone agent are described separately
without presenting them as unrelated engagements; the Go research is retained.

No planned-project details were supplied, so that section says none are listed
rather than inventing commitments. Replace that line with your confirmed plans.

`preview.html` approximates GitHub's layout, not its sanitizer or live deployment.
Its light/dark controls set the containing page's color scheme; the SVG images
respond to the inherited scheme in supporting browsers. To regenerate its
article from `README.md`:

```sh
uv run --no-cache tools/build_profile_preview.py
```

Open `preview.html` locally to inspect the profile, and open
`windows-xp-profile.html` for the desktop. The banner link in the preview still
points to the public Pages URL and requires the setup above. Check the README
on GitHub after publication, including the mobile and reduced-motion versions.

The previous painting assets remain in the repository, unchanged. The README
no longer displays that painting as its banner, so the old top-of-page artwork
caption has been removed. The personal-interest text still names Aivazovsky's
*Ship on a Stormy Sea* (1858).
