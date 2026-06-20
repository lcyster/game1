import os
from io import BytesIO
from pathlib import Path
from typing import Any, TypedDict, cast

import requests
import wikipedia
from PIL import Image
from flask import Flask, Response, jsonify, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename


JsonObject = dict[str, Any]


class WikiData(TypedDict):
    summary: str
    image: str | None


ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
PLACEHOLDER_VALUES = {'TREFLE_API_KEY': 'your_trefle_api_key_here'}


def load_environment_files() -> None:
    environment_values: dict[str, str] = {}
    for environment_path in [Path.home() / '.env.game1', ROOT_DIRECTORY / '.env']:
        environment_values.update(read_environment_file(environment_path, set()))

    for environment_name, environment_value in environment_values.items():
        current_value = os.environ.get(environment_name)
        placeholder_value = PLACEHOLDER_VALUES.get(environment_name)
        if current_value is None or current_value == placeholder_value:
            os.environ[environment_name] = environment_value


def read_environment_file(environment_path: Path, visited_paths: set[Path]) -> dict[str, str]:
    expanded_path = environment_path.expanduser()
    if not expanded_path.exists():
        return {}

    resolved_path = expanded_path.resolve()
    if resolved_path in visited_paths:
        return {}

    visited_paths.add(resolved_path)
    environment_values: dict[str, str] = {}

    for environment_line in expanded_path.read_text(encoding='utf-8').splitlines():
        stripped_line = environment_line.strip()
        if not stripped_line or stripped_line.startswith('#'):
            continue

        if stripped_line.startswith('source '):
            source_path = Path(os.path.expanduser(stripped_line.removeprefix('source ').strip()))
            if not source_path.is_absolute():
                source_path = expanded_path.parent / source_path
            environment_values.update(read_environment_file(source_path, visited_paths))
            continue

        if stripped_line.startswith('export '):
            stripped_line = stripped_line.removeprefix('export ').strip()

        if '=' not in stripped_line:
            continue

        environment_name, environment_value = stripped_line.split('=', 1)
        environment_name = environment_name.strip()
        environment_value = unquote_environment_value(environment_value.strip())
        if environment_name:
            environment_values[environment_name] = environment_value

    return environment_values


def unquote_environment_value(environment_value: str) -> str:
    if len(environment_value) >= 2 and environment_value[0] == environment_value[-1] and environment_value[0] in {'"', "'"}:
        return environment_value[1:-1]
    return environment_value


load_environment_files()

app = Flask(__name__)

cache: dict[str, JsonObject | WikiData] = {}

base_directory = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_directory, '..', 'instance', 'plants.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.config.root_path, 'static', 'uploads')

db = SQLAlchemy(app)

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo_filename = db.Column(db.String(100))
    wiki_link = db.Column(db.String(200))

@app.route('/')
def index() -> str:
    plants = Plant.query.all()
    return render_template('index.html', plants=plants)

@app.route('/add')
def add_plant() -> str:
    return render_template('add_plant.html')

@app.route('/api/add-plant-from-trefle', methods=['POST'])
def add_plant_from_trefle() -> Response:
    request_data = request.get_json(silent=True)
    if not isinstance(request_data, dict):
        return jsonify({'error': 'Expected JSON object.'})

    name = request_data.get('name')
    scientific_name = request_data.get('scientific_name')
    if not isinstance(name, str):
        return jsonify({'error': 'Plant name is required.'})
    if scientific_name is not None and not isinstance(scientific_name, str):
        return jsonify({'error': 'Scientific name must be a string.'})

    trefle_data = get_plant_info(name)
    image_url = get_trefle_image_url(trefle_data)
    wiki_name = scientific_name or name

    if image_url:
        photo_filename = cache_plant_image(image_url, wiki_name)
    else:
        wiki_data = get_wiki_data(wiki_name)
        photo_filename = cache_plant_image(wiki_data['image'], wiki_name) if wiki_data['image'] else None

    new_plant = cast(Any, Plant)(name=name, photo_filename=photo_filename, wiki_link=f"https://en.wikipedia.org/wiki/{wiki_name.replace(' ', '_')}")
    db.session.add(new_plant)
    db.session.commit()

    return jsonify({'url': url_for('plant_overview', plant_id=new_plant.id)})

@app.route('/plant/<int:plant_id>')
def plant_overview(plant_id: int) -> str:
    plant = Plant.query.get_or_404(plant_id)
    trefle_data = get_plant_info(plant.name)
    wiki_data = get_wiki_data(plant.name)
    wiki_summary = wiki_data['summary']

    return render_template('plant_overview.html', plant=plant, trefle_data=trefle_data, wiki_summary=wiki_summary)

def get_wiki_data(plant_name: str) -> WikiData:
    cache_key = f"wiki_{plant_name}"
    if cache_key in cache:
        return cast(WikiData, cache[cache_key])

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


TREFLE_API_KEY = os.environ.get('TREFLE_API_KEY')

def get_plant_info(plant_name: str) -> JsonObject:
    cache_key = f"trefle_{plant_name}"
    if cache_key in cache:
        return cast(JsonObject, cache[cache_key])

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
        return cast(JsonObject, cache[cache_key])

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


def cache_plant_image(image_url: str, plant_name: str) -> str | None:
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(image_url, stream=True, headers=headers)
        response.raise_for_status()

        safe_filename = secure_filename(plant_name) + ".jpg"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'images', safe_filename)

        with Image.open(BytesIO(response.content)) as image:
            image.thumbnail((300, 300))
            image.save(image_path, 'JPEG', quality=85)

        return os.path.join('images', safe_filename)
    except requests.exceptions.RequestException as exception:
        print(f"Error downloading image: {exception}")
    except OSError as exception:
        print(f"Error processing image: {exception}")

    return None

@app.route('/api/plant-info/<plant_name>')
def plant_info(plant_name: str) -> Response:
    return jsonify(search_plants(plant_name))

@app.cli.command("init-db")
def init_db_command() -> None:
    db.create_all()
    print("Initialized the database.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
