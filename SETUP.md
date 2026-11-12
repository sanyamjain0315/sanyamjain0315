# Install the profile

Copy `README.md` and the `assets` folder into the root of your public
`sanyamjain0315/sanyamjain0315` repository and commit them together.
The profile will use the README automatically.

Open `preview.html` locally to view the animation before uploading. The preview
approximates GitHub's Markdown layout; it is not a separate portfolio website.
Use its theme buttons to inspect both versions.

The painting is the original supplied JPEG, copied without re-encoding. It is
embedded unchanged in both header SVGs and displayed in full at its original
aspect ratio. No filters, overlays, crops, or animation affect the painting.

The SVG typography eases into place once on page load. Thin ornamental lines
move slowly outside the painting. The animation uses CSS inside SVG images,
without JavaScript, external fonts, services, or GitHub Actions. Reduced-motion
preferences disable all SVG animations. Projects and interests remain native,
selectable README text.

To change the name or header text, edit `tools/build_assets.py` and run:

```sh
python3 tools/build_assets.py
```

The preview, setup notes, and build script do not have to be uploaded to GitHub.
The supplied artwork is credited to Ivan Aivazovsky, *Ship on a Stormy Sea* (1858).
