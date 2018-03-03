from config import app, db
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    dateTime = db.Column(db.DateTime)
    tags = db.Column(db.String(200))

    def __repr__(self):
        return '<Topic %r>' % self.name