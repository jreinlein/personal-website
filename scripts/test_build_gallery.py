"""Unit tests for build_gallery.py — independent of the gitignored originals/.

Run with: python -m pytest scripts/test_build_gallery.py -v
"""

from datetime import datetime

from PIL import Image, ImageOps

from build_gallery import (
    interpolate_missing_dates,
    parse_override_date,
    resize_stripped,
    verify_stripped,
)


def make_geotagged_jpeg(path, size=(400, 300)):
    """Write a JPEG with DateTimeOriginal + GPS EXIF, mimicking an iPhone photo."""
    img = Image.new("RGB", size, color="red")
    exif = img.getexif()
    exif[306] = "2024:01:03 10:44:19"  # DateTime
    gps_ifd = {1: "N", 2: (40.0, 44.0, 0.0), 3: "W", 4: (73.0, 58.0, 0.0)}
    exif[0x8825] = gps_ifd
    img.save(path, "JPEG", exif=exif.tobytes())


def test_fixture_actually_has_gps(tmp_path):
    """Sanity check the fixture itself — a vacuous strip test proves nothing."""
    src = tmp_path / "IMG_0001.jpg"
    make_geotagged_jpeg(src)
    with Image.open(src) as img:
        exif = img.getexif()
        assert exif.get_ifd(0x8825), "fixture must carry GPS EXIF for this test to mean anything"


def test_resize_stripped_removes_gps_and_all_exif(tmp_path):
    src = tmp_path / "IMG_0001.jpg"
    make_geotagged_jpeg(src)

    with Image.open(src) as img:
        base = ImageOps.exif_transpose(img).convert("RGB")

    clean = resize_stripped(base, 200, "width")
    out_path = tmp_path / "out.webp"
    clean.save(out_path, "WEBP", quality=80)

    assert verify_stripped(out_path)


def test_resize_stripped_preserves_aspect_ratio_width_mode(tmp_path):
    src = tmp_path / "IMG_0001.jpg"
    make_geotagged_jpeg(src, size=(400, 200))
    with Image.open(src) as img:
        base = ImageOps.exif_transpose(img).convert("RGB")

    result = resize_stripped(base, 100, "width")
    assert result.size == (100, 50)


def test_resize_stripped_preserves_aspect_ratio_long_edge_mode(tmp_path):
    src = tmp_path / "IMG_0001.jpg"
    make_geotagged_jpeg(src, size=(200, 400))
    with Image.open(src) as img:
        base = ImageOps.exif_transpose(img).convert("RGB")

    result = resize_stripped(base, 100, "long_edge")
    assert result.size == (50, 100)


def test_resize_stripped_does_not_upscale(tmp_path):
    src = tmp_path / "IMG_0001.jpg"
    make_geotagged_jpeg(src, size=(100, 80))
    with Image.open(src) as img:
        base = ImageOps.exif_transpose(img).convert("RGB")

    result = resize_stripped(base, 1600, "long_edge")
    assert result.size == (100, 80)


def test_interpolate_missing_dates_brackets_from_neighbours():
    photos = [
        {"filename": "IMG_0997.jpg", "date": datetime(2024, 1, 3, 10, 44, 19), "date_interpolated": False},
        {"filename": "IMG_0998.jpg", "date": None, "date_interpolated": False},
        {"filename": "IMG_0999.jpg", "date": datetime(2024, 1, 3, 10, 45, 58), "date_interpolated": False},
    ]
    result = interpolate_missing_dates(photos)
    middle = next(p for p in result if p["filename"] == "IMG_0998.jpg")
    assert middle["date"] == datetime(2024, 1, 3, 10, 45, 8, 500000)
    assert middle["date_interpolated"] is True


def test_interpolate_missing_dates_uses_single_neighbour_at_edge():
    photos = [
        {"filename": "IMG_0001.jpg", "date": None, "date_interpolated": False},
        {"filename": "IMG_0002.jpg", "date": datetime(2024, 1, 3, 10, 0, 0), "date_interpolated": False},
    ]
    result = interpolate_missing_dates(photos)
    first = next(p for p in result if p["filename"] == "IMG_0001.jpg")
    assert first["date"] == datetime(2024, 1, 3, 10, 0, 0)
    assert first["date_interpolated"] is True


def test_parse_override_date_formats():
    assert parse_override_date("2023") == datetime(2023, 1, 1)
    assert parse_override_date("2023-06") == datetime(2023, 6, 1)
    assert parse_override_date("2023-06-15") == datetime(2023, 6, 15)
