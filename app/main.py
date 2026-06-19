import os
import requests
import wikipedia
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'instance', 'plants.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.config.root_path, 'static', 'uploads')

db = SQLAlchemy(app)

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo_filename = db.Column(db.String(100))
    wiki_link = db.Column(db.String(200))

@app.route('/')
def index():
    plants = Plant.query.all()
    plant_data = []
    for plant in plants:
        trefle_data = get_plant_info(plant.name)
        
        scientific_name = None
        if trefle_data and trefle_data.get('data') and len(trefle_data['data']) > 0:
            scientific_name = trefle_data['data'][0].get('scientific_name')
        
        wiki_data = get_wiki_data(scientific_name or plant.name)

        image_url = None
        if trefle_data and trefle_data.get('data') and len(trefle_data['data']) > 0 and trefle_data['data'][0].get('image_url'):
            image_url = trefle_data['data'][0]['image_url']
        elif wiki_data['image']:
            image_url = wiki_data['image']
        elif plant.photo_filename:
            image_url = url_for('static', filename='uploads/' + plant.photo_filename)

        plant_data.append({'plant': plant, 'trefle_data': trefle_data, 'image_url': image_url})
    return render_template('index.html', plant_data=plant_data)

@app.route('/add')
def add_plant():
    return render_template('add_plant.html')

@app.route('/api/add-plant-from-trefle', methods=['POST'])
def add_plant_from_trefle():
    data = request.json
    name = data.get('name')
    scientific_name = data.get('scientific_name')
    image_url = data.get('image_url')

    new_plant = Plant(name=name, photo_filename=image_url, wiki_link=f"https://en.wikipedia.org/wiki/{scientific_name.replace(' ', '_')}")
    db.session.add(new_plant)
    db.session.commit()

    return jsonify({'url': url_for('plant_overview', plant_id=new_plant.id)})

@app.route('/plant/<int:plant_id>')
def plant_overview(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    trefle_data = get_plant_info(plant.name)
    
    scientific_name = None
    if trefle_data and trefle_data.get('data') and len(trefle_data['data']) > 0:
        scientific_name = trefle_data['data'][0].get('scientific_name')

    wiki_data = get_wiki_data(scientific_name or plant.name)
    wiki_summary = wiki_data['summary']

    image_url = None
    if trefle_data and trefle_data.get('data') and len(trefle_data['data']) > 0 and trefle_data['data'][0].get('image_url'):
        image_url = trefle_data['data'][0]['image_url']
    elif wiki_data['image']:
        image_url = wiki_data['image']
    elif plant.photo_filename:
        image_url = url_for('static', filename='uploads/' + plant.photo_filename)

    return render_template('plant_overview.html', plant=plant, trefle_data=trefle_data, wiki_summary=wiki_summary, image_url=image_url)

def get_wiki_data(plant_name):
    try:
        page = wikipedia.page(plant_name, auto_suggest=False)
        summary = wikipedia.summary(plant_name, sentences=2)
        image = page.images[0] if page.images else None
        return {'summary': summary, 'image': image}
    except wikipedia.exceptions.PageError:
        return {'summary': "Could not find a Wikipedia page for this plant.", 'image': None}
    except wikipedia.exceptions.DisambiguationError as e:
        return {'summary': f"Multiple Wikipedia pages found. Please be more specific: {e.options}", 'image': None}
    except requests.exceptions.JSONDecodeError:
        return {'summary': "Could not parse the response from Wikipedia.", 'image': None}


TREFLE_API_KEY = os.environ.get('TREFLE_API_KEY')

def get_plant_info(plant_name):
    if not TREFLE_API_KEY:
        return {"error": "Trefle API key not configured."}

    search_url = f"https://trefle.io/api/v1/plants/search?token={TREFLE_API_KEY}&q={plant_name}"
    
    try:
        search_response = requests.get(search_url)
        search_response.raise_for_status()
        search_results = search_response.json()

        if not search_results['data']:
            return {"error": "Plant not found."}

        return search_results
    except requests.exceptions.RequestException as e:
        print(f"Error fetching plant data: {e}")
        return {"error": str(e)}

@app.route('/api/plant-info/<plant_name>')
def plant_info(plant_name):
    return jsonify(get_plant_info(plant_name))

# A command to initialize the database
@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables."""
    db.create_all()
    print("Initialized the database.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
