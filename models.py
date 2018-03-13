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

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column('user_id', db.Integer, db.ForeignKey("topic.id"), nullable=False)
    name = db.Column(db.Text)
    option1 = db.Column(db.String(80), nullable=False)
    option2 = db.Column(db.String(80), nullable=False)
    option3 = db.Column(db.String(80), nullable=False)
    option4 = db.Column(db.String(80), nullable=False)
    correct_answer = db.Column(db.SmallInteger, nullable=False)

    def __repr__(self):
        return '<Question %r>' % self.question