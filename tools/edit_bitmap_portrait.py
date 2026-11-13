# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "opencv-python-headless", "pillow"]
# ///
"""Create grayscale bitmap art: uv run --no-cache tools/edit_bitmap_portrait.py.

Uses OpenCV for tonal processing and serpentine Floyd–Steinberg dithering
for a true black-and-white bitmap texture, without cropping the source.
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "20260913_032405.jpg"
OUTPUT = ROOT / "assets" / f"{SOURCE.stem}-bitmap"


def dither(gray):
    pixels = gray.astype(np.float32).copy()
    height, width = pixels.shape
    result = np.zeros((height, width), dtype=np.uint8)
    # Alternating scan direction avoids the diagonal streaks of a one-way
    # diffusion pass while keeping grain deterministic and image-derived.
    for y in range(height):
        direction = 1 if y % 2 == 0 else -1
        columns = range(width) if direction == 1 else range(width - 1, -1, -1)
        for x in columns:
            old = pixels[y, x]
            new = 1.0 if old >= 0.5 else 0.0
            result[y, x] = 255 if new else 0
            error = old - new
            ahead = x + direction
            behind = x - direction
            if 0 <= ahead < width:
                pixels[y, ahead] += error * 7 / 16
            if y + 1 < height:
                if 0 <= behind < width:
                    pixels[y + 1, behind] += error * 3 / 16
                pixels[y + 1, x] += error * 5 / 16
                if 0 <= ahead < width:
                    pixels[y + 1, ahead] += error / 16
    return result


def main():
    with Image.open(SOURCE) as image:
        rgb = np.array(ImageOps.exif_transpose(image).convert("RGB"))
    height, width = rgb.shape[:2]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 22, 5)
    local = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8)).apply(gray)
    gray = cv2.addWeighted(gray, 0.7, local, 0.3, 0).astype(np.float32) / 255
    black, white = np.percentile(gray, [1, 99])
    tone = np.clip((gray - black) / max(float(white - black), 0.01), 0, 1)
    tone = np.power(tone, 1.05)
    tone = np.clip((tone - 0.5) * 1.08 + 0.5, 0, 1)

    # Dither at a lower resolution, then preserve the square pixels with
    # nearest-neighbor scaling instead of smoothing away the bitmap texture.
    factor = min(1.0, 720 / max(width, height))
    small = cv2.resize(tone, (round(width * factor), round(height * factor)),
                       interpolation=cv2.INTER_AREA)
    bitmap = cv2.resize(dither(small), (width, height), interpolation=cv2.INTER_NEAREST)
    image = Image.fromarray(bitmap).convert("1", dither=Image.Dither.NONE)
    for suffix in (".png", ".bmp"):
        path = OUTPUT.with_suffix(suffix)
        image.save(path)
        with Image.open(path) as check:
            check.load()
            assert check.size == (width, height) and check.mode == "1"
        print(f"Saved and verified 1-bit image: {path.relative_to(ROOT)} ({width} × {height})")
    print(f"Source unchanged: {SOURCE.name}")


if __name__ == "__main__":
    main()
