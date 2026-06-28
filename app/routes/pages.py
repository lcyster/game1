import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Blueprint, Response, jsonify, render_template, send_from_directory

from app.models import Plant, db
from app.image_cache import get_or_create_cached_image
from app.distribution_map import get_distribution_country_codes


pages_blueprint = Blueprint('pages', __name__)

TREFLE_API_KEY = os.environ.get('TREFLE_API_KEY')


def get_trefle_family_species_count(family_name: str) -> int | None:
    if not TREFLE_API_KEY:
        return None
    try:
        url = f"https://trefle.io/api/v1/species?token={TREFLE_API_KEY}&filter[family_name]={family_name}"
        request = Request(url)
        response = urlopen(request, timeout=5)
        import json
        data = json.loads(response.read())
        meta = data.get('meta')
        if isinstance(meta, dict):
            total = meta.get('total')
            if isinstance(total, int):
                return total
    except Exception:
        pass
    return None


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
    wiki_data = get_wiki_data(plant.scientific_name or plant.name)
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
            db.session.commit()

    if not plant.family:
        species_data = trefle_data.get('data')
        if isinstance(species_data, dict):
            family_data = species_data.get('family')
            if isinstance(family_data, str):
                plant.family = family_data
                db.session.commit()

    image_path, image_width, image_height = get_or_create_cached_image(plant)
    distribution_countries = get_distribution_country_codes(trefle_data)
    return render_template('plant_overview.html', plant=plant, trefle_data=trefle_data, wiki_summary=wiki_summary, image_width=image_width, image_height=image_height, distribution_countries=distribution_countries)


@pages_blueprint.route('/cache/<int:plant_id>/<int:size>')
def serve_cached_image(plant_id: int, size: int):
    plant = Plant.query.get_or_404(plant_id)
    image_path, width, height = get_or_create_cached_image(plant, size)
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


@pages_blueprint.route('/groups')
def groups() -> str:
    family_rows = (
        db.session.query(Plant.family, db.func.count(Plant.id))
        .filter(Plant.family.isnot(None))
        .group_by(Plant.family)
        .order_by(Plant.family)
        .all()
    )
    badges = []
    for family_name, found_count in family_rows:
        total_count = get_trefle_family_species_count(family_name)
        undiscovered = (total_count - found_count) if total_count is not None else None
        representative_plant = (
            Plant.query.filter_by(family=family_name)
            .order_by(Plant.name)
            .first()
        )
        badges.append({
            'family': family_name,
            'found_count': found_count,
            'undiscovered': undiscovered,
            'representative_plant': representative_plant,
        })
    return render_template('groups.html', badges=badges)


@pages_blueprint.route('/groups/<family_name>')
def family_detail(family_name: str) -> str:
    plants = Plant.query.filter_by(family=family_name).order_by(Plant.name).all()
    return render_template('family_detail.html', family_name=family_name, plants=plants)
