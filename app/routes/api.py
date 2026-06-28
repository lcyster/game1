from pathlib import Path
from typing import Any, cast

from flask import Blueprint, Response, jsonify, request, url_for
from werkzeug.utils import secure_filename

from app.config import INSTANCE_DIRECTORY
from app.models import Plant, db, clean_scientific_name
from app.photo_gps import extract_gps
from app.trefle import get_plant_info, get_trefle_image_url, search_plants
from app.wikipedia import get_wiki_data


api_blueprint = Blueprint('api', __name__, url_prefix='/api')

UPLOAD_DIRECTORY = INSTANCE_DIRECTORY / 'uploads'


@api_blueprint.route('/add-plant-from-trefle', methods=['POST'])
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

    existing_plant = Plant.query.filter_by(scientific_name=scientific_name).first()
    if existing_plant:
        return jsonify({'error': 'A plant with this species already exists.'}), 409

    trefle_data = get_plant_info(name)
    image_url = get_trefle_image_url(trefle_data)
    wiki_name = scientific_name or name

    family = None
    species_data = trefle_data.get('data')
    if isinstance(species_data, dict):
        family_data = species_data.get('family')
        if isinstance(family_data, str):
            family = family_data

    if not image_url:
        wiki_data = get_wiki_data(wiki_name)
        image_url = wiki_data['image']

    new_plant = cast(Any, Plant)(
        name=name,
        scientific_name=scientific_name,
        family=family,
        wiki_link=f"https://en.wikipedia.org/wiki/{wiki_name.replace(' ', '_')}",
        image_source_url=image_url,
        added_lat=request_data.get('lat'),
        added_lng=request_data.get('lng'),
    )
    db.session.add(new_plant)
    db.session.commit()

    return jsonify({'url': url_for('pages.plant_overview', plant_id=new_plant.id)})


@api_blueprint.route('/plant-info/<plant_name>')
def plant_info(plant_name: str) -> Response:
    return jsonify(search_plants(plant_name))


@api_blueprint.route('/upload-plant-photo', methods=['POST'])
def upload_plant_photo() -> Response:
    name = request.form.get('name')
    scientific_name = request.form.get('scientific_name')
    if not isinstance(name, str) or not name.strip():
        return jsonify({'error': 'Plant name is required.'})

    photo = request.files.get('photo')
    if not photo or not photo.filename:
        return jsonify({'error': 'A photo is required.'})

    existing_plant = Plant.query.filter_by(scientific_name=scientific_name).first()
    if existing_plant:
        return jsonify({'error': 'A plant with this species already exists.'}), 409

    photo_bytes = photo.read()
    gps = extract_gps(photo_bytes)

    directory_name = clean_scientific_name(scientific_name or name).lower()
    upload_dir = UPLOAD_DIRECTORY / directory_name
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = secure_filename(photo.filename)
    extension = Path(safe_filename).suffix.lower() or '.jpg'
    photo_path = upload_dir / f"{directory_name}{extension}"
    photo_path.write_bytes(photo_bytes)

    trefle_data = get_plant_info(name)
    family = None
    species_data = trefle_data.get('data')
    if isinstance(species_data, dict):
        family_data = species_data.get('family')
        if isinstance(family_data, str):
            family = family_data

    wiki_name = scientific_name or name
    new_plant = cast(Any, Plant)(
        name=name,
        scientific_name=scientific_name,
        family=family,
        wiki_link=f"https://en.wikipedia.org/wiki/{wiki_name.replace(' ', '_')}",
        image_source_url=str(photo_path),
        added_lat=gps[0] if gps else None,
        added_lng=gps[1] if gps else None,
    )
    db.session.add(new_plant)
    db.session.commit()

    return jsonify({
        'url': url_for('pages.plant_overview', plant_id=new_plant.id),
        'gps': {'lat': gps[0], 'lng': gps[1]} if gps else None,
    })


@api_blueprint.route('/clear-plants', methods=['POST'])
def clear_plants() -> Response:
    Plant.query.delete()
    db.session.commit()
    return jsonify({'ok': True})
