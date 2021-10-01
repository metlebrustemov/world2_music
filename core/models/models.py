import os
from .application import create_application

app, db = create_application()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    u_token = db.Column(db.String(100), default="0", nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class W2Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,nullable=False)
    name = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(120), unique=True, nullable=False)
    is_public = db.Column(db.Boolean(), default=True, nullable=False)
    u_name = db.Column(db.String(100), unique=True, nullable=False) #unikal name
    m_token = db.Column(db.String(100), default="0", nullable=False)

    def __repr__(self):
        return '<W2Media %r>' % self.u_name
