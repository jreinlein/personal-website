#!/usr/bin/env python3
"""Build pottery gallery derivatives from originals/.

Scans originals/*.jpg, reads EXIF date + dimensions, resizes to two WebP
sizes with all metadata stripped, and updates pottery.json with stubs for
any newly seen photo. Full regen every run — see docs/pottery-gallery-plan.md.
"""

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ORIGINALS_DIR = ROOT / "originals"
OUTPUT_DIR = ROOT / "img" / "pottery"
THUMB_DIR = OUTPUT_DIR / "thumb"
LARGE_DIR = OUTPUT_DIR / "large"
POTTERY_JSON = ROOT / "pottery.json"

THUMB_WIDTH = 500
THUMB_QUALITY = 75
LARGE_LONG_EDGE = 1600
LARGE_QUALITY = 80

EXIF_IFD_TAG = 0x8769  # points to the sub-IFD that holds DateTimeOriginal
DATETIME_ORIGINAL = 36867
DATETIME_FALLBACK = 306


def read_exif_date(image):
    exif = image.getexif()
    exif_ifd = exif.get_ifd(EXIF_IFD_TAG)
    raw = exif_ifd.get(DATETIME_ORIGINAL) or exif.get(DATETIME_FALLBACK)
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None


def interpolate_missing_dates(photos):
    """Fill missing dates from filename-adjacent neighbours.

    iPhone IMG_#### names increase monotonically within a session, so a gap
    between two dated shots is a reliable stand-in for a lost EXIF date.
    """
    ordered = sorted(photos, key=lambda p: p["filename"])
    for i, photo in enumerate(ordered):
        if photo["date"] is not None:
            continue
        prev_date = next(
            (ordered[j]["date"] for j in range(i - 1, -1, -1) if ordered[j]["date"]),
            None,
        )
        next_date = next(
            (ordered[j]["date"] for j in range(i + 1, len(ordered)) if ordered[j]["date"]),
            None,
        )
        if prev_date and next_date:
            photo["date"] = prev_date + (next_date - prev_date) / 2
            photo["date_interpolated"] = True
        elif prev_date or next_date:
            photo["date"] = prev_date or next_date
            photo["date_interpolated"] = True
    return ordered


def parse_override_date(value):
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date override: {value!r}")


def resize_stripped(base, max_dim, mode):
    """Resize `base` (already EXIF-transposed) and return a metadata-free copy.

    Building a fresh Image via new()+paste() guarantees no EXIF/ICC/GPS chunk
    from the source rides along, rather than trusting WebP save() to drop it.
    """
    width, height = base.size
    if mode == "width":
        new_width = min(width, max_dim)
        new_height = round(height * (new_width / width))
    else:  # long_edge
        scale = min(1.0, max_dim / max(width, height))
        new_width = round(width * scale)
        new_height = round(height * scale)

    resized = base.resize((new_width, new_height), Image.LANCZOS)
    clean = Image.new(resized.mode, resized.size)
    clean.paste(resized)
    return clean


def load_pottery_json():
    if POTTERY_JSON.exists():
        return json.loads(POTTERY_JSON.read_text(encoding="utf-8"))
    return {}


def verify_stripped(path):
    with Image.open(path) as img:
        exif = img.getexif()
        has_gps = bool(exif.get_ifd(0x8825))  # GPS IFD tag
        return len(exif) == 0 and not has_gps


def main():
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    LARGE_DIR.mkdir(parents=True, exist_ok=True)

    sidecar = load_pottery_json()
    files = sorted(set(ORIGINALS_DIR.glob("*.jpg")) | set(ORIGINALS_DIR.glob("*.JPG")))

    photos = []
    for path in files:
        with Image.open(path) as img:
            date = read_exif_date(img)
            width, height = ImageOps.exif_transpose(img).size
        photos.append(
            {
                "filename": path.name,
                "path": path,
                "date": date,
                "width": width,
                "height": height,
                "date_interpolated": False,
            }
        )

    photos = interpolate_missing_dates(photos)

    unresolved = []
    for photo in photos:
        entry = sidecar.get(photo["filename"], {})
        if "date" in entry:
            photo["date"] = parse_override_date(entry["date"])
            photo["date_interpolated"] = False
        if photo["date"] is None:
            unresolved.append(photo["filename"])

    for photo in photos:
        with Image.open(photo["path"]) as img:
            base = ImageOps.exif_transpose(img).convert("RGB")

        thumb = resize_stripped(base, THUMB_WIDTH, "width")
        thumb_path = THUMB_DIR / f"{photo['path'].stem}.webp"
        thumb.save(thumb_path, "WEBP", quality=THUMB_QUALITY)

        large = resize_stripped(base, LARGE_LONG_EDGE, "long_edge")
        large_path = LARGE_DIR / f"{photo['path'].stem}.webp"
        large.save(large_path, "WEBP", quality=LARGE_QUALITY)

    for photo in photos:
        sidecar.setdefault(photo["filename"], {})
    POTTERY_JSON.write_text(
        json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    photos.sort(key=lambda p: (p["date"] or datetime.min, p["filename"]), reverse=True)

    not_stripped = [
        f.name
        for f in list(THUMB_DIR.glob("*.webp")) + list(LARGE_DIR.glob("*.webp"))
        if not verify_stripped(f)
    ]

    total_bytes = sum(f.stat().st_size for f in THUMB_DIR.glob("*.webp"))
    total_bytes += sum(f.stat().st_size for f in LARGE_DIR.glob("*.webp"))

    print(f"Processed {len(photos)} photos.")
    interpolated = [p["filename"] for p in photos if p["date_interpolated"]]
    if interpolated:
        print(f"Interpolated dates for: {', '.join(interpolated)}")
    if unresolved:
        print(f"UNRESOLVED dates (add a pottery.json override): {', '.join(unresolved)}")
    if not_stripped:
        print(f"WARNING: EXIF/GPS still present in: {', '.join(not_stripped)}")
    else:
        print("Verified: no EXIF/GPS data in any derivative.")
    print(f"Derivative output: {total_bytes / 1_000_000:.1f} MB in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
