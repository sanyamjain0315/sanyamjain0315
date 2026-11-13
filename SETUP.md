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
checked-in snapshots generated from GitHub's public REST API. They are visible
immediately, even before automation is enabled. The mobile layout is selected
below 600px and keeps an intrinsic width of 420px instead of stretching.

- Scope: **all public repositories owned by `sanyamjain0315`**, including forks,
  archived repositories, and this profile repository. Private repositories and
  repositories owned by other accounts/organizations are not included.
- Every language reported by GitHub is displayed. Notebook files remain
  **Jupyter Notebook**; their bytes are not reassigned to Python.
- The percentages sum **language bytes**, not repository counts, commits,
  proficiency, or time spent. Large notebooks and repeated fork code can
  dominate the result. A tiny language can round to `0.00%` without being
  excluded.
- `assets/languages.json` contains the repository inventory, totals, scope,
  retrieval timestamp, and exact underlying counts.

### Automatic weekly refresh

Publish `.github/workflows/language-stats.yml` and
`tools/build_language_stats.py` along with the assets. Enable **GitHub Actions**
for the repository. The workflow runs on Mondays at **06:17 UTC**, and can also
be run manually from **Actions → Refresh public repository languages → Run
workflow**. Scheduled runs can be delayed by GitHub.

The workflow uses the automatic `GITHUB_TOKEN` and requests write access only
for its refresh job, to commit the three generated assets back to `main`. No PAT,
third-party stats account, paid service, or private-repository access is needed.
Repository/organization policies must allow that token to push to `main`; branch
protection may require you to regenerate the files locally and submit a PR
instead. Public API requests are rate-limited; optional `GITHUB_TOKEN` also works
locally to increase the limit. Never put a token in a checked-in file.

To refresh locally with Python 3.11+:

```sh
python3 tools/build_language_stats.py
```

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
