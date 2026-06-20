#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def backfill_images():
    """Downloads, compresses, and saves images for existing plants."""
    import requests
    from PIL import Image
    from app.main import app, db, Plant, get_plant_info, get_wiki_data
    from werkzeug.utils import secure_filename

    with app.app_context():
        plants = Plant.query.all()
        for plant in plants:
            if not plant.photo_filename or not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], plant.photo_filename)):
                print(f"Processing {plant.name}...")
                trefle_data = get_plant_info(plant.name)
                image_url = None
                if trefle_data and trefle_data.get('data') and trefle_data['data'].get('image_url'):
                    image_url = trefle_data['data']['image_url']
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

                        with Image.open(response.raw) as img:
                            img.thumbnail((300, 300))
                            img.save(image_path, 'JPEG', quality=85)
                        
                        plant.photo_filename = os.path.join('images', safe_filename)
                        print(f"  Image saved to {image_path}")

                    except requests.exceptions.RequestException as e:
                        print(f"  Error downloading image: {e}")
                    except IOError as e:
                        print(f"  Error processing image: {e}")
        
        db.session.commit()
        print("Finished backfilling images.")


def main():
    parser = argparse.ArgumentParser(
        description="Download, resize, and cache missing images for existing plants."
    )
    parser.parse_args()
    backfill_images()


if __name__ == '__main__':
    main()
