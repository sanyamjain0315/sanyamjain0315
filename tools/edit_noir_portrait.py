# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "opencv-python-headless", "pillow-heif"]
# ///
"""Run with: uv run --no-cache tools/edit_noir_portrait.py

A non-destructive, source-specific OpenCV edit inspired by the supplied
high-contrast, grainy monochrome portrait. No generated facial features.
"""
from pathlib import Path

import cv2
import numpy as np
import pillow_heif
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "20260913_032405.heic"
OUTPUT = ROOT / "assets" / f"{SOURCE.stem}-noir"
SIZE = 1800


def blur(image, sigma):
    return cv2.GaussianBlur(image, (0, 0), sigma)


def ellipse_light(x, y, cx, cy, rx, ry):
    return np.exp(-0.5 * (((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2))


def main():
    pillow_heif.register_heif_opener()
    with Image.open(SOURCE) as image:
        rgb = np.array(ImageOps.exif_transpose(image).convert("RGB"))
    height, width = rgb.shape[:2]

    # Center the new three-quarter portrait without including the shoulders.
    crop_x, crop_y, crop_size = width * 0.045, height * 0.095, width * 0.90
    scale = SIZE / crop_size
    transform = np.float32([[scale, 0, -crop_x * scale], [0, scale, -crop_y * scale]])
    portrait = cv2.warpAffine(rgb, transform, (SIZE, SIZE), flags=cv2.INTER_AREA)
    gray = cv2.cvtColor(portrait, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255

    # Follow this photo's hairline, temples, ear and jaw; feather inward to
    # suppress the colorful backdrop and keep the neck out of the light.
    face_outline = np.float32([
        [.318, .308], [.390, .291], [.490, .310], [.562, .347],
        [.613, .361], [.654, .405], [.676, .455], [.693, .479],
        [.731, .461], [.763, .466], [.778, .502], [.766, .552],
        [.747, .587], [.704, .615], [.688, .663], [.656, .721],
        [.616, .767], [.557, .808], [.487, .830], [.419, .817],
        [.364, .788], [.321, .742], [.299, .688], [.284, .623],
        [.277, .558], [.267, .496], [.270, .429], [.285, .370],
    ])
    points = face_outline * np.float32([width, height])
    points = cv2.transform(points[None], transform)[0].round().astype(np.int32)
    mask = np.zeros((SIZE, SIZE), np.uint8)
    cv2.fillPoly(mask, [points], 255)
    distance = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    matte = blur(np.clip(distance / 24, 0, 1), 10)

    yy, xx = np.mgrid[:SIZE, :SIZE].astype(np.float32)
    # Work in original photo coordinates so the lighting remains aligned
    # with the face if output resolution changes.
    x = (xx / scale + crop_x) / width
    y = (yy / scale + crop_y) / height
    light = (
        0.10
        + 1.15 * ellipse_light(x, y, .430, .365, .140, .075)
        + 0.85 * ellipse_light(x, y, .412, .548, .055, .085)
        + 1.00 * ellipse_light(x, y, .337, .600, .062, .090)
        + 1.05 * ellipse_light(x, y, .439, .767, .095, .042)
        + 0.50 * ellipse_light(x, y, .592, .578, .048, .065)
    )
    # Retain real facial modelling, but soften skin detail before the grain.
    soft = blur(gray, 9)
    # This indoor photo is darker than the previous daylight source; derive
    # the usable tonal range from the face, not the surrounding background.
    low, high = np.percentile(soft[matte > 0.9], [6, 98])
    relief = np.clip((soft - low) / max(float(high - low), 0.01), 0, 1)
    exposed = relief * light
    tone = 1 / (1 + np.exp(-10 * (exposed - 0.43)))
    face = blur(tone * matte, 4.5)

    # A faint halo and multi-scale film grain echo the reference's rough
    # highlight boundaries without applying a binary threshold to the face.
    halo = blur(face, 37) * 0.035
    rng = np.random.default_rng(316)
    fine = rng.normal(0, 1, (SIZE, SIZE)).astype(np.float32)
    coarse = rng.normal(0, 1, (SIZE // 3, SIZE // 3)).astype(np.float32)
    coarse = cv2.resize(coarse, (SIZE, SIZE), interpolation=cv2.INTER_LINEAR)
    coarse /= coarse.std()
    grain = 0.40 * fine + 0.80 * coarse
    amplitude = 0.012 + 0.19 * np.sqrt(np.clip(face, 0, 1))
    image = face * 0.91 + halo + 0.009 + grain * amplitude
    # Slight paper-like density variation, kept subtle in the black field.
    texture = blur(rng.normal(0, 1, (SIZE, SIZE)).astype(np.float32), 2)
    image += texture * 0.025
    output = np.uint8(np.clip(image, 0, 1) * 255)

    png, jpg = OUTPUT.with_suffix(".png"), OUTPUT.with_suffix(".jpg")
    for path, params in [(png, []), (jpg, [cv2.IMWRITE_JPEG_QUALITY, 95])]:
        if not cv2.imwrite(str(path), output, params):
            raise RuntimeError(f"Could not write {path}")
        decoded = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        assert decoded is not None and decoded.shape == (SIZE, SIZE)
        print(f"Saved and decoded: {path.relative_to(ROOT)} ({SIZE} × {SIZE})")
    print(f"Source preserved: {SOURCE.name}")


if __name__ == "__main__":
    main()
