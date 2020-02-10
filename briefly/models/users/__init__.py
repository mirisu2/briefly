from briefly import db
from datetime import datetime


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_email = db.Column(db.String(255), nullable=False)
    user_token = db.Column(db.String(255), unique=True, nullable=False)
    user_reg_ip = db.Column(db.String(15), nullable=False)
