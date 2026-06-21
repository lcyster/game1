import os
import re
import subprocess
import sys
import time
from io import BytesIO
from pathlib import Path
from typing import Any, TypedDict, cast

import requests
import wikipedia
from PIL import Image
from flask import Flask, Response, jsonify, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from sqlalchemy import text


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


def get_git_info() -> tuple[str, bool | None]:
    commitish = os.environ.get('GIT_COMMITISH')
    dirty_value = os.environ.get('GIT_DIRTY')

    if commitish and dirty_value is not None:
        dirty = dirty_value.lower() in ('true', '1', 'yes')
        return commitish, dirty

    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            check=False,
            cwd=ROOT_DIRECTORY,
        )
        git_commitish = result.stdout.strip() if result.returncode == 0 else 'unknown'
    except FileNotFoundError:
        git_commitish = 'unknown'

    if dirty_value is not None:
        dirty = dirty_value.lower() in ('true', '1', 'yes')
    else:
        try:
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT_DIRECTORY,
            )
            dirty = bool(status_result.stdout.strip()) if status_result.returncode == 0 else None
        except FileNotFoundError:
            dirty = None

    return commitish or git_commitish, dirty


load_environment_files()

app = Flask(__name__)

cache: dict[str, JsonObject | WikiData] = {}

base_directory = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_directory, '..', 'instance', 'plants.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.config.root_path, 'static', 'uploads')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

with app.app_context():
    upgrade()

STARTUP_COMMITISH, STARTUP_DIRTY = get_git_info()

RELOAD_MODE = 'disabled' if ('--no-reload' in sys.argv or not app.debug) else 'enabled'


class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo_filename = db.Column(db.String(100))
    wiki_link = db.Column(db.String(200))
    image_source_url = db.Column(db.String(200))
    scientific_name = db.Column(db.String(100))


def get_static_directory() -> Path:
    if app.static_folder:
        return Path(app.static_folder)
    return Path(app.root_path) / 'static'


def normalize_photo_filename(photo_filename: str | None) -> str | None:
    if not photo_filename:
        return None

    normalized_filename = photo_filename.replace('\\', '/').lstrip('/')
    if normalized_filename.startswith('http://') or normalized_filename.startswith('https://'):
        return None

    if (get_static_directory() / normalized_filename).exists():
        return normalized_filename

    if not normalized_filename.startswith('uploads/'):
        upload_relative_filename = (Path('uploads') / normalized_filename).as_posix()
        if (get_static_directory() / upload_relative_filename).exists() or normalized_filename.startswith('images/'):
            return upload_relative_filename

    return normalized_filename


def photo_file_exists(photo_filename: str | None) -> bool:
    normalized_filename = normalize_photo_filename(photo_filename)
    if not normalized_filename:
        return False
    return (get_static_directory() / normalized_filename).exists()

@app.route('/')
def index() -> str:
    plants = Plant.query.all()
    has_normalized_photo_filename = False
    for plant in plants:
        normalized_photo_filename = normalize_photo_filename(plant.photo_filename)
        if normalized_photo_filename != plant.photo_filename:
            plant.photo_filename = normalized_photo_filename
            has_normalized_photo_filename = True

    if has_normalized_photo_filename:
        db.session.commit()

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

    if not image_url:
        wiki_data = get_wiki_data(wiki_name)
        image_url = wiki_data['image']

    name_for_image = scientific_name or wiki_name
    photo_filename = cache_plant_image(image_url, name_for_image) if image_url else None

    new_plant = cast(Any, Plant)(
        name=name,
        scientific_name=scientific_name,
        photo_filename=photo_filename,
        wiki_link=f"https://en.wikipedia.org/wiki/{wiki_name.replace(' ', '_')}",
        image_source_url=image_url,
    )
    db.session.add(new_plant)
    db.session.commit()

    return jsonify({'url': url_for('plant_overview', plant_id=new_plant.id)})

@app.route('/plant/<int:plant_id>')
def plant_overview(plant_id: int) -> str:
    plant = Plant.query.get_or_404(plant_id)
    trefle_data = get_plant_info(plant.name)
    wiki_data = get_wiki_data(plant.name)
    wiki_summary = wiki_data['summary']
    has_plant_changes = False

    normalized_photo_filename = normalize_photo_filename(plant.photo_filename)
    if normalized_photo_filename != plant.photo_filename:
        plant.photo_filename = normalized_photo_filename
        has_plant_changes = True

    if not plant.photo_filename or not photo_file_exists(plant.photo_filename):
        image_url = plant.image_source_url or get_trefle_image_url(trefle_data)
        if not image_url:
            image_url = wiki_data['image']

        if image_url:
            scientific_name = plant.scientific_name
            if not scientific_name:
                species_data = trefle_data.get('data')
                if isinstance(species_data, dict):
                    species_scientific_name = species_data.get('scientific_name')
                    if isinstance(species_scientific_name, str):
                        scientific_name = species_scientific_name

            name_to_use = scientific_name if scientific_name else plant.name

            photo_filename = cache_plant_image(image_url, name_to_use)
            if photo_filename:
                plant.photo_filename = photo_filename
                plant.image_source_url = image_url
                if not plant.scientific_name and scientific_name:
                    plant.scientific_name = scientific_name
                has_plant_changes = True

    if has_plant_changes:
        db.session.commit()

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


def clean_scientific_name(name: str) -> str:
    cleaned_name = re.sub(r'[^a-zA-Z0-9_]+', '_', name).strip('_')
    return cleaned_name or 'plant'

def cache_plant_image(image_url: str, scientific_name: str) -> str | None:
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(image_url, stream=True, headers=headers)
        response.raise_for_status()

        with Image.open(BytesIO(response.content)) as image:
            image.thumbnail((300, 300))

            timestamp = int(time.time())
            dimensions = f"{image.width}x{image.height}"
            cleaned_name = clean_scientific_name(scientific_name)

            safe_filename = f"{cleaned_name}_{dimensions}_{timestamp}.jpg"
            upload_directory = Path(app.config['UPLOAD_FOLDER']) / 'images'
            image_path = upload_directory / safe_filename

            upload_directory.mkdir(parents=True, exist_ok=True)
            image.save(image_path, 'JPEG', quality=85)

        return (Path('uploads') / 'images' / safe_filename).as_posix()
    except requests.exceptions.RequestException as exception:
        print(f"Error downloading image: {exception}")
    except OSError as exception:
        print(f"Error processing image: {exception}")

    return None

@app.route('/api/plant-info/<plant_name>')
def plant_info(plant_name: str) -> Response:
    return jsonify(search_plants(plant_name))

@app.route('/debug/plant/<int:plant_id>')
def debug_plant(plant_id: int) -> Response:
    plant = Plant.query.get_or_404(plant_id)
    return jsonify({
        'id': plant.id,
        'name': plant.name,
        'photo_filename': plant.photo_filename,
        'wiki_link': plant.wiki_link,
        'image_source_url': plant.image_source_url,
        'scientific_name': plant.scientific_name,
    })

@app.route('/health')
def health() -> tuple[Response, int]:
    try:
        db.session.execute(text('SELECT 1'))
        status = 'ok'
        status_code = 200
    except Exception:
        status = 'error'
        status_code = 503

    return jsonify({
        'status': status,
        'commitish': STARTUP_COMMITISH,
        'dirty': STARTUP_DIRTY,
        'reload': RELOAD_MODE,
    }), status_code

@app.cli.command("init-db")
def init_db_command() -> None:
    db.create_all()
    print("Initialized the database.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
