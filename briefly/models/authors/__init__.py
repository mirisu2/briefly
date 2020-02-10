from briefly import db


class Authors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_fullname = db.Column(db.String(255), unique=True, nullable=False)
    author_url = db.Column(db.String(255), unique=True, nullable=False)
