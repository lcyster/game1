from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

from app.config import CACHE_DIRECTORY
from app.models import Plant, clean_scientific_name


def get_cached_image_path(plant: Plant, size: int = 300) -> Path:
    directory_name = clean_scientific_name(plant.scientific_name or plant.name).lower()
    timestamp = int(plant.updated_at.timestamp()) if plant.updated_at else 0
    return CACHE_DIRECTORY / directory_name / f'{directory_name}_{size}x{size}_{timestamp}.jpg'


def download_and_cache(image_url: str, cache_path: Path, size: int) -> tuple[Path, int, int]:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(image_url, stream=True, headers=headers)
    response.raise_for_status()

    with Image.open(BytesIO(response.content)) as image:
        source_width, source_height = image.size
        actual_size = min(size, source_width, source_height)
        image.thumbnail((actual_size, actual_size))
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(cache_path, 'JPEG', quality=85)
        final_width, final_height = image.size

    return cache_path, final_width, final_height


def get_or_create_cached_image(plant: Plant, size: int = 300) -> tuple[Path, int, int]:
    cache_path = get_cached_image_path(plant, size)
    if cache_path.exists():
        with Image.open(cache_path) as image:
            width, height = image.size
        return cache_path, width, height

    if not plant.image_source_url:
        from flask import current_app
        static_folder = current_app.static_folder
        if static_folder is None:
            raise RuntimeError("Static folder not configured")
        placeholder_path = Path(static_folder) / 'placeholder.png'
        with Image.open(placeholder_path) as image:
            width, height = image.size
        return placeholder_path, width, height

    return download_and_cache(plant.image_source_url, cache_path, size)
