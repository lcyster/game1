from typing import Any, cast

from flask import Blueprint, Response, jsonify, request, url_for

from app.models import Plant, db
from app.trefle import get_plant_info, get_trefle_image_url, search_plants
from app.wikipedia import get_wiki_data


api_blueprint = Blueprint('api', __name__, url_prefix='/api')


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

    trefle_data = get_plant_info(name)
    image_url = get_trefle_image_url(trefle_data)
    wiki_name = scientific_name or name

    if not image_url:
        wiki_data = get_wiki_data(wiki_name)
        image_url = wiki_data['image']

    new_plant = cast(Any, Plant)(
        name=name,
        scientific_name=scientific_name,
        wiki_link=f"https://en.wikipedia.org/wiki/{wiki_name.replace(' ', '_')}",
        image_source_url=image_url,
    )
    db.session.add(new_plant)
    db.session.commit()

    return jsonify({'url': url_for('pages.plant_overview', plant_id=new_plant.id)})


@api_blueprint.route('/plant-info/<plant_name>')
def plant_info(plant_name: str) -> Response:
    return jsonify(search_plants(plant_name))
