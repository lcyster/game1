from io import BytesIO
from typing import Any

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS


def _rational_to_float(value: Any) -> float | None:
    if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
        if value.denominator == 0:
            return None
        return float(value.numerator) / float(value.denominator)
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _dms_to_decimal(dms: Any, ref: str) -> float | None:
    parts = [_rational_to_float(v) for v in dms]
    if not all(parts) or len(parts) != 3:
        return None
    degrees, minutes, seconds = parts
    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if ref in ('S', 'W'):
        decimal = -decimal
    return decimal


def _get_gps_tag_name(tag_id: int) -> str | None:
    return GPSTAGS.get(tag_id)


def extract_gps(image_bytes: bytes) -> tuple[float, float] | None:
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            exif_data = image.getexif()
            if not exif_data:
                return None

            gps_ifd = exif_data.get_ifd(0x8825)
            if not gps_ifd:
                return None

            latitude = None
            longitude = None
            lat_ref = None
            lng_ref = None

            for key_id, value in gps_ifd.items():
                tag_name = _get_gps_tag_name(key_id)
                if tag_name == 'GPSLatitude':
                    latitude = value
                elif tag_name == 'GPSLongitude':
                    longitude = value
                elif tag_name == 'GPSLatitudeRef':
                    lat_ref = value
                elif tag_name == 'GPSLongitudeRef':
                    lng_ref = value

            if latitude and longitude and lat_ref and lng_ref:
                lat = _dms_to_decimal(latitude, lat_ref)
                lng = _dms_to_decimal(longitude, lng_ref)
                if lat is not None and lng is not None:
                    return (lat, lng)

    except Exception:
        pass

    return None
