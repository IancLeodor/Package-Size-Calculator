from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT

db = SQLAlchemy()

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    length = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    processed_image = db.Column(LONGTEXT, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
