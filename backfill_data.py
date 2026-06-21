import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def backfill_data():
    from app import create_app
    from app.models import Plant, db
    from app.trefle import get_plant_info
    from app.wikipedia import get_wiki_data

    app = create_app()
    with app.app_context():
        plants = Plant.query.all()
        for plant in plants:
            print(f"Processing {plant.name}...")
            trefle_data = get_plant_info(plant.name)
            wiki_data = get_wiki_data(plant.name)

            plant.image_source_url = None
            if trefle_data and trefle_data.get('data') and trefle_data['data'].get('image_url'):
                plant.image_source_url = trefle_data['data']['image_url']
            elif wiki_data['image']:
                plant.image_source_url = wiki_data['image']

            plant.scientific_name = trefle_data.get('data', {}).get('scientific_name')
            plant.wiki_link = f"https://en.wikipedia.org/wiki/{plant.name.replace(' ', '_')}"

            if plant.image_source_url:
                print(f"  Updated image source URL for {plant.name}")

        db.session.commit()
        print("Finished backfilling data.")


if __name__ == '__main__':
    backfill_data()
