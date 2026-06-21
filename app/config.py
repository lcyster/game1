import os
from pathlib import Path


ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
INSTANCE_DIRECTORY = ROOT_DIRECTORY / 'instance'
CACHE_DIRECTORY = INSTANCE_DIRECTORY / 'cache'


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_DIRECTORY, 'plants.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
