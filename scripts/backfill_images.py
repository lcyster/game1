#!/usr/bin/env python3

import argparse
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def backfill_images() -> None:
    from app import create_app
    from app.models import Plant, db

    app = create_app()
    with app.app_context():
        plants = Plant.query.all()
        for plant in plants:
            if not plant.image_source_url:
                print(f"Processing {plant.name}...")
                time.sleep(1)
                from app.trefle import get_plant_info, get_trefle_image_url
                from app.wikipedia import get_wiki_data

                trefle_data = get_plant_info(plant.name)
                image_url: str | None = None
                trefle_species_data = trefle_data.get('data')
                if isinstance(trefle_species_data, dict):
                    trefle_image_url = trefle_species_data.get('image_url')
                    if isinstance(trefle_image_url, str):
                        image_url = trefle_image_url
                else:
                    wiki_data = get_wiki_data(plant.name)
                    if wiki_data['image']:
                        image_url = wiki_data['image']

                if image_url:
                    plant.image_source_url = image_url
                    if not plant.scientific_name:
                        from typing import Any, cast
                        species_data = trefle_data.get('data')
                        if isinstance(species_data, dict):
                            species_scientific_name = cast(dict[str, Any], species_data).get('scientific_name')
                            if isinstance(species_scientific_name, str):
                                plant.scientific_name = species_scientific_name
                    print(f"  Updated image source URL for {plant.name}")

        db.session.commit()
        print("Finished backfilling images.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download, resize, and cache missing images for existing plants."
    )
    parser.parse_args()
    backfill_images()


if __name__ == '__main__':
    main()
