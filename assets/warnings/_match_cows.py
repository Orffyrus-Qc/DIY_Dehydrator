"""Crop diamonds, remove exterior white, match sizes for README."""
from pathlib import Path

import numpy as np
from PIL import Image

SOURCES = {
    "zone": Path(r"E:\myDATA\IMAGES\falling_cow_zone1.jpg"),
    "award": Path(r"E:\myDATA\IMAGES\falling-cow-award.gif"),
}
if not SOURCES["zone"].exists():
    SOURCES["zone"] = Path("falling_cow_zone1.jpg")
if not SOURCES["award"].exists():
    SOURCES["award"] = Path("falling-cow-award.png")

TARGET = 420
PAD = 6
DARK = (28, 28, 32, 255)


def flood_transparent(im: Image.Image, tol: int = 35) -> Image.Image:
    """Exterior near-white -> transparent via flood fill from edges."""
    rgba = im.convert("RGBA")
    a = np.array(rgba)
    h, w = a.shape[:2]
    rgb = a[:, :, :3].astype(np.int16)
    near_white = (
        (rgb[:, :, 0] >= 255 - tol)
        & (rgb[:, :, 1] >= 255 - tol)
        & (rgb[:, :, 2] >= 255 - tol)
    )

    visited = np.zeros((h, w), dtype=bool)
    stack = [(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]
    step_x = max(1, w // 80)
    step_y = max(1, h // 80)
    for x in range(0, w, step_x):
        stack.append((0, x))
        stack.append((h - 1, x))
    for y in range(0, h, step_y):
        stack.append((y, 0))
        stack.append((y, w - 1))

    while stack:
        y, x = stack.pop()
        if y < 0 or y >= h or x < 0 or x >= w or visited[y, x]:
            continue
        if not near_white[y, x]:
            continue
        visited[y, x] = True
        stack.extend([(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)])

    a[visited, 3] = 0

    # Kill remaining pure-white (not yellow diamond, not black ink)
    is_yellowish = (rgb[:, :, 0] > 200) & (rgb[:, :, 1] > 140) & (rgb[:, :, 2] < 130)
    is_blackish = (rgb[:, :, 0] < 45) & (rgb[:, :, 1] < 45) & (rgb[:, :, 2] < 45)
    kill = near_white & ~is_yellowish & ~is_blackish
    a[kill, 3] = 0

    return Image.fromarray(a, "RGBA")


def crop_to_alpha(im: Image.Image, pad: int = PAD) -> Image.Image:
    arr = np.array(im)
    ys, xs = np.where(arr[:, :, 3] > 10)
    if len(xs) == 0:
        return im
    y0, y1 = int(ys.min()), int(ys.max())
    x0, x1 = int(xs.min()), int(xs.max())
    y0 = max(0, y0 - pad)
    x0 = max(0, x0 - pad)
    y1 = min(arr.shape[0] - 1, y1 + pad)
    x1 = min(arr.shape[1] - 1, x1 + pad)
    return im.crop((x0, y0, x1 + 1, y1 + 1))


def fit_square(im: Image.Image, size: int = TARGET) -> Image.Image:
    im = im.copy()
    im.thumbnail((size - 2, size - 2), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - im.width) // 2
    y = (size - im.height) // 2
    canvas.paste(im, (x, y), im)
    return canvas


def process(path: Path, out_name: str) -> Image.Image:
    im = Image.open(path)
    if getattr(im, "n_frames", 1) > 1:
        im.seek(0)
    im = flood_transparent(im, tol=40)
    im = crop_to_alpha(im)
    im = fit_square(im)
    im.save(out_name, "PNG", optimize=True)
    arr = np.array(im)
    print(
        out_name,
        im.size,
        "corner",
        arr[0, 0].tolist(),
        "opaque%",
        round(100 * (arr[:, :, 3] > 10).mean(), 1),
    )
    return im


def on_dark(im: Image.Image, name: str) -> None:
    bg = Image.new("RGBA", im.size, DARK)
    bg.alpha_composite(im)
    bg.convert("RGB").save(name, "JPEG", quality=92)
    print("wrote", name, Image.open(name).size)


def main() -> None:
    zone = process(SOURCES["zone"], "falling_cow_zone1.png")
    award = process(SOURCES["award"], "falling-cow-award.png")

    gap = 28
    banner_w = TARGET * 2 + gap
    banner = Image.new("RGBA", (banner_w, TARGET), DARK)
    banner.paste(zone, (0, 0), zone)
    banner.paste(award, (TARGET + gap, 0), award)
    banner.save("falling_cow_pair_banner.png", "PNG", optimize=True)
    banner.convert("RGB").save("falling_cow_pair_banner.jpg", "JPEG", quality=92)
    print("banner", banner.size)

    on_dark(zone, "falling_cow_zone1_matched.jpg")
    on_dark(award, "falling-cow-award_matched.jpg")
    print("done")


if __name__ == "__main__":
    main()
