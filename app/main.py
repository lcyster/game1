import os
import requests
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
    return render_template('index.html', plants=plants)

@app.route('/add', methods=['GET', 'POST'])
def add_plant():
    if request.method == 'POST':
        name = request.form['name']
        wiki_link = request.form['wiki_link']
        photo = request.files['photo']
        
        photo_filename = None
        if photo:
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        new_plant = Plant(name=name, wiki_link=wiki_link, photo_filename=photo_filename)
        db.session.add(new_plant)
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('add_plant.html')

TREFLE_API_KEY = os.environ.get('TREFLE_API_KEY')

@app.route('/api/plant-info/<plant_name>')
def plant_info(plant_name):
    if not TREFLE_API_KEY:
        return jsonify({"error": "Trefle API key not configured."}), 500

    url = f"https://trefle.io/api/v1/plants/search?token={TREFLE_API_KEY}&q={plant_name}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

# A command to initialize the database
@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables."""
    db.create_all()
    print("Initialized the database.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
