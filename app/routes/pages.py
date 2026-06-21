from flask import Blueprint, Response, jsonify, render_template, send_from_directory

from app.models import Plant
from app.image_cache import get_or_create_cached_image


pages_blueprint = Blueprint('pages', __name__)


@pages_blueprint.route('/')
def index() -> str:
    plants = Plant.query.all()
    return render_template('index.html', plants=plants)


@pages_blueprint.route('/add')
def add_plant() -> str:
    return render_template('add_plant.html')


@pages_blueprint.route('/plant/<int:plant_id>')
def plant_overview(plant_id: int) -> str:
    plant = Plant.query.get_or_404(plant_id)
    from app.trefle import get_plant_info, get_trefle_image_url
    from app.wikipedia import get_wiki_data

    trefle_data = get_plant_info(plant.name)
    wiki_data = get_wiki_data(plant.name)
    wiki_summary = wiki_data['summary']

    if not plant.image_source_url:
        image_url = get_trefle_image_url(trefle_data)
        if not image_url:
            image_url = wiki_data['image']

        if image_url:
            plant.image_source_url = image_url
            scientific_name = plant.scientific_name
            if not scientific_name:
                species_data = trefle_data.get('data')
                if isinstance(species_data, dict):
                    species_scientific_name = species_data.get('scientific_name')
                    if isinstance(species_scientific_name, str):
                        scientific_name = species_scientific_name
            if not plant.scientific_name and scientific_name:
                plant.scientific_name = scientific_name
            from app.models import db
            db.session.commit()

    return render_template('plant_overview.html', plant=plant, trefle_data=trefle_data, wiki_summary=wiki_summary)


@pages_blueprint.route('/cache/<int:plant_id>/<int:size>')
def serve_cached_image(plant_id: int, size: int):
    plant = Plant.query.get_or_404(plant_id)
    image_path = get_or_create_cached_image(plant, size)
    return send_from_directory(image_path.parent, image_path.name)


@pages_blueprint.route('/debug/plant/<int:plant_id>')
def debug_plant(plant_id: int) -> Response:
    plant = Plant.query.get_or_404(plant_id)
    return jsonify({
        'id': plant.id,
        'name': plant.name,
        'wiki_link': plant.wiki_link,
        'image_source_url': plant.image_source_url,
        'scientific_name': plant.scientific_name,
    })
