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


def download_and_cache(image_url: str, cache_path: Path, size: int) -> Path:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(image_url, stream=True, headers=headers)
    response.raise_for_status()

    with Image.open(BytesIO(response.content)) as image:
        image.thumbnail((size, size))
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(cache_path, 'JPEG', quality=85)

    return cache_path


def get_or_create_cached_image(plant: Plant, size: int = 300) -> Path:
    cache_path = get_cached_image_path(plant, size)
    if cache_path.exists():
        return cache_path

    if not plant.image_source_url:
        from flask import current_app
        static_folder = current_app.static_folder
        if static_folder is None:
            raise RuntimeError("Static folder not configured")
        return Path(static_folder) / 'placeholder.png'

    return download_and_cache(plant.image_source_url, cache_path, size)
