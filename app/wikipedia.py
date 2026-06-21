from typing import TypedDict

import requests
import wikipedia


class WikiData(TypedDict):
    summary: str
    image: str | None


cache: dict[str, WikiData] = {}


def get_wiki_data(plant_name: str) -> WikiData:
    cache_key = f"wiki_{plant_name}"
    if cache_key in cache:
        return cache[cache_key]

    try:
        page = wikipedia.page(plant_name, auto_suggest=False)
        summary = wikipedia.summary(plant_name, sentences=2)
        image = page.images[0] if page.images else None
        data: WikiData = {'summary': str(summary), 'image': str(image) if image else None}
        cache[cache_key] = data
        return data
    except wikipedia.exceptions.PageError:
        return {'summary': "Could not find a Wikipedia page for this plant.", 'image': None}
    except wikipedia.exceptions.DisambiguationError as exception:
        return {'summary': f"Multiple Wikipedia pages found. Please be more specific: {exception.options}", 'image': None}
    except requests.exceptions.JSONDecodeError:
        return {'summary': "Could not parse the response from Wikipedia.", 'image': None}
