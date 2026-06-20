import os
import requests
from PIL import Image
from app.main import app, db, Plant, get_plant_info, get_wiki_data
from werkzeug.utils import secure_filename

def backfill_data():
    """Fills in the new data fields for existing plants."""
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

            plant.common_name = trefle_data.get('data', {}).get('common_name')
            plant.scientific_name = trefle_data.get('data', {}).get('scientific_name')
            plant.family = trefle_data.get('data', {}).get('family', {}).get('name')
            plant.genus = trefle_data.get('data', {}).get('genus', {}).get('name')
            plant.native_distribution = ",".join(trefle_data.get('data', {}).get('distribution', {}).get('native', []))
            plant.wiki_summary = wiki_data['summary']

            if plant.image_source_url and (not plant.photo_filename or not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], plant.photo_filename))):
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                    response = requests.get(plant.image_source_url, stream=True, headers=headers)
                    response.raise_for_status()

                    safe_filename = secure_filename(plant.scientific_name or plant.name) + ".jpg"
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
        print("Finished backfilling data.")

if __name__ == '__main__':
    backfill_data()
