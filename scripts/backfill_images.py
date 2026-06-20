#!/usr/bin/env python3

import argparse
import os
import sys
import time
from io import BytesIO
from pathlib import Path
from typing import Any, cast


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def backfill_images() -> None:
    import requests
    from PIL import Image
    from app.main import app, db, Plant, get_plant_info, get_wiki_data
    from werkzeug.utils import secure_filename

    with app.app_context():
        plants = Plant.query.all()
        for plant in plants:
            if plant.photo_filename and '\\' in plant.photo_filename:
                print(f"Fixing path for {plant.name}...")
                plant.photo_filename = plant.photo_filename.replace('\\', '/')
                db.session.add(plant)

            if not plant.photo_filename or not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], plant.photo_filename)):
                print(f"Processing {plant.name}...")
                time.sleep(1)
                trefle_data = get_plant_info(plant.name)
                image_url: str | None = None
                trefle_species_data = trefle_data.get('data')
                if isinstance(trefle_species_data, dict):
                    trefle_image_url = cast(dict[str, Any], trefle_species_data).get('image_url')
                    if isinstance(trefle_image_url, str):
                        image_url = trefle_image_url
                else:
                    wiki_data = get_wiki_data(plant.name)
                    if wiki_data['image']:
                        image_url = wiki_data['image']

                if image_url:
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                        response = requests.get(image_url, stream=True, headers=headers)
                        response.raise_for_status()

                        safe_filename = secure_filename(plant.name) + ".jpg"
                        image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'images', safe_filename)

                        os.makedirs(os.path.dirname(image_path), exist_ok=True)

                        with Image.open(BytesIO(response.content)) as image:
                            image.thumbnail((300, 300))
                            image.save(image_path, 'JPEG', quality=85)
                        
                        plant.photo_filename = (Path('images') / safe_filename).as_posix()
                        plant.image_source_url = image_url
                        print(f"  Image saved to {image_path}")

                    except requests.exceptions.RequestException as exception:
                        print(f"  Error downloading image: {exception}")
                    except OSError as exception:
                        print(f"  Error processing image: {exception}")
        
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
