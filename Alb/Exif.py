"""
EXIF data extraction for album images.
Requires Pillow (py3-pillow on Alpine).
"""

import logging
import math
import pathlib

logger = logging.getLogger(__name__)

# EXIF tags we care about, mapped to friendly names
_TAGS = {
    "FNumber":              "aperture",
    "FocalLength":          "focal_length",
    "ISOSpeedRatings":      "iso",
    "ExposureTime":         "shutter",
    "ExposureBiasValue":    "exposure_bias",
    "Flash":                "flash",
    "WhiteBalance":         "white_balance",
    "LensModel":            "lens",
    "Model":                "camera",
    "Make":                 "make",
    "DateTime":             "datetime",
    "DateTimeOriginal":     "datetime_original",
    "GPSInfo":              "gps",
}

def _ratio(val):
    """Convert an IFDRational or tuple (num, den) to a float."""
    try:
        return float(val)
    except Exception:
        pass
    try:
        num, den = val
        return num / den if den else 0
    except Exception:
        return None

def _format_aperture(val):
    f = _ratio(val)
    if f is None:
        return None
    return f"f/{f:.1f}"

def _format_focal(val):
    f = _ratio(val)
    if f is None:
        return None
    # Drop trailing zero after decimal if whole number
    if f == int(f):
        return f"{int(f)} mm"
    return f"{f:.1f} mm"

def _format_shutter(val):
    """Return a human-readable shutter speed like '1/250 s' or '2 s'."""
    f = _ratio(val)
    if f is None:
        return None
    if f >= 1:
        return f"{f:.0f} s"
    # Express as 1/N
    n = round(1 / f)
    return f"1/{n} s"

def _parse_gps(gps_raw):
    """
    Parse the GPSInfo IFD dict from Pillow into a dict with lat, lon, alt.
    GPS IFD keys are integers. Standard mapping:
      1 = GPSLatitudeRef, 2 = GPSLatitude, 3 = GPSLongitudeRef, 4 = GPSLongitude
      5 = GPSAltitudeRef, 6 = GPSAltitude
    """
    def dms_to_deg(dms):
        d = _ratio(dms[0])
        m = _ratio(dms[1])
        s = _ratio(dms[2])
        if d is None or m is None or s is None:
            return None
        return d + m / 60 + s / 3600

    try:
        lat = dms_to_deg(gps_raw[2])
        lon = dms_to_deg(gps_raw[4])
        if lat is None or lon is None:
            return None
        if gps_raw.get(1, "N") == "S":
            lat = -lat
        if gps_raw.get(3, "E") == "W":
            lon = -lon
        result = {"lat": lat, "lon": lon}
        if 6 in gps_raw:
            alt = _ratio(gps_raw[6])
            if alt is not None:
                if gps_raw.get(5, 0) == 1:
                    alt = -alt
                result["alt"] = round(alt, 1)
        return result
    except Exception as e:
        logger.debug(f"GPS parse error: {e}")
        return None

def read(path: pathlib.Path) -> dict:
    """
    Read EXIF data from an image file. Returns a dict with fields:
      aperture, focal_length, iso, shutter, exposure_bias, flash,
      camera, lens, datetime, gps (sub-dict with lat/lon/alt).
    Returns an empty dict if EXIF cannot be read.
    """
    try:
        from PIL import Image, ExifTags
    except ImportError:
        logger.warning("Pillow not installed; EXIF data unavailable. Install py3-pillow.")
        return {}

    try:
        img = Image.open(path)
        raw = img._getexif()
        if raw is None:
            return {}
    except Exception as e:
        logger.info(f"EXIF read failed for {path}: {e}")
        return {}

    # Build tag-name → value dict
    tag_map = {ExifTags.TAGS.get(k, k): v for k, v in raw.items()}

    result = {}

    if "FNumber" in tag_map:
        result["aperture"] = _format_aperture(tag_map["FNumber"])

    if "FocalLength" in tag_map:
        result["focal_length"] = _format_focal(tag_map["FocalLength"])

    if "ISOSpeedRatings" in tag_map:
        result["iso"] = f"ISO {tag_map['ISOSpeedRatings']}"

    if "ExposureTime" in tag_map:
        result["shutter"] = _format_shutter(tag_map["ExposureTime"])

    if "ExposureBiasValue" in tag_map:
        ev = _ratio(tag_map["ExposureBiasValue"])
        if ev is not None and ev != 0:
            result["exposure_bias"] = f"{ev:+.1f} EV"

    if "Model" in tag_map:
        cam = tag_map["Model"].strip()
        make = tag_map.get("Make", "").strip()
        # Avoid duplicating make in model string (e.g. "Canon Canon EOS …")
        if make and not cam.startswith(make):
            cam = f"{make} {cam}"
        result["camera"] = cam

    if "LensModel" in tag_map:
        result["lens"] = tag_map["LensModel"].strip()

    # Prefer DateTimeOriginal (when the shutter fired) over DateTime (file write)
    for dt_key in ("DateTimeOriginal", "DateTime"):
        if dt_key in tag_map:
            result["datetime"] = tag_map[dt_key]
            break

    if "GPSInfo" in tag_map:
        gps = _parse_gps(tag_map["GPSInfo"])
        if gps:
            result["gps"] = gps

    # Remove None values
    return {k: v for k, v in result.items() if v is not None}
