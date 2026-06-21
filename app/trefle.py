import os
from typing import Any, cast

import requests


JsonObject = dict[str, Any]

TREFLE_API_KEY = os.environ.get('TREFLE_API_KEY')

cache: dict[str, JsonObject] = {}


def get_plant_info(plant_name: str) -> JsonObject:
    cache_key = f"trefle_{plant_name}"
    if cache_key in cache:
        return cache[cache_key]

    search_results = search_plants(plant_name)
    search_data = search_results.get('data')
    if not isinstance(search_data, list) or not search_data:
        return {"error": "Plant not found."}

    first_search_result = search_data[0]
    if not isinstance(first_search_result, dict):
        return {"error": "Plant not found."}

    plant_slug = first_search_result.get('slug')
    if not isinstance(plant_slug, str):
        return {"error": "Plant not found."}

    if not TREFLE_API_KEY:
        return {"error": "Trefle API key not configured."}

    try:
        species_url = f"https://trefle.io/api/v1/species/{plant_slug}?token={TREFLE_API_KEY}"
        species_response = requests.get(species_url)
        species_response.raise_for_status()
        species_data = cast(JsonObject, species_response.json())

        cache[cache_key] = species_data
        return species_data
    except requests.exceptions.RequestException as exception:
        print(f"Error fetching plant data: {exception}")
        return {"error": str(exception)}


def search_plants(plant_name: str) -> JsonObject:
    cache_key = f"trefle_search_{plant_name}"
    if cache_key in cache:
        return cache[cache_key]

    if not TREFLE_API_KEY:
        return {"error": "Trefle API key not configured."}

    search_url = f"https://trefle.io/api/v1/plants/search?token={TREFLE_API_KEY}&q={plant_name}"

    try:
        search_response = requests.get(search_url)
        search_response.raise_for_status()
        search_results = cast(JsonObject, search_response.json())
        cache[cache_key] = search_results
        return search_results
    except requests.exceptions.RequestException as exception:
        print(f"Error fetching plant data: {exception}")
        return {"error": str(exception)}


def get_trefle_image_url(trefle_data: JsonObject) -> str | None:
    species_data = trefle_data.get('data')
    if not isinstance(species_data, dict):
        return None

    image_url = species_data.get('image_url')
    return image_url if isinstance(image_url, str) else None
