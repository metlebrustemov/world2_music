from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from ..constants import M_UPLOAD_FOLDER, DB_NAME, KEY_NAME

def create_application():
    app = Flask(__name__)
    app.secret_key = b'HbfGMYwEOnLdm3USo5k7JRAzn0P3oVEHPdLSoNKku3qmKfWUjt6tsgbbnPuoYWmXNiGIjpyXtm7DZ1DbAYxx1F8LmerBW1DsaeSf'
    db_path = os.path.join(os.path.dirname(__file__), '{}'.format(DB_NAME))
    db_uri = 'sqlite:///{}'.format(db_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    key_path = os.path.join(os.path.dirname(__file__), '{}'.format(KEY_NAME))
    app.config["KEY_FILE_PATH"] = key_path
    app.config['UPLOAD_FOLDER'] = M_UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 40 * 1000 * 1000 #uploaded file max size
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db = SQLAlchemy(app)
    return app, db
