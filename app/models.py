import re
from datetime import datetime, timezone

from flask import url_for
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def clean_scientific_name(name: str) -> str:
    cleaned_name = re.sub(r'[^a-zA-Z0-9_]+', '_', name).strip('_')
    return cleaned_name or 'plant'


class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    wiki_link = db.Column(db.String(512))
    image_source_url = db.Column(db.String(2048))
    scientific_name = db.Column(db.String(256))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def get_image_url(self, size: int = 300) -> str:
        if not self.image_source_url:
            return url_for('static', filename='placeholder.png')
        return url_for('pages.serve_cached_image', plant_id=self.id, size=size)
