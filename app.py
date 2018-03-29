from flask import Flask, render_template, request, url_for, redirect
from flask_socketio import SocketIO
from flask_socketio import emit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import Topic, Question
from config import app, db

socketio = SocketIO(app)

@app.route('/topics')
def display_all():
    topics = Topic.query.all()
    return render_template("all.html", topics=topics)

@app.route('/review/<int:topic_id>')
def review(topic_id):
    questions = Question.query.filter_by(topic_id=topic_id)
    return render_template("review.html", questions=questions, topic_id=topic_id)

@app.route('/')
def landing():
    topics = Topic.query.all()
    return render_template("landing.html", topics=topics)

@app.route('/startquiz', methods = ['GET', 'POST'])
def startquiz():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        date = request.form.get('date')
        time = request.form.get('time')
        dateTime = datetime.strptime(date+time, "%Y-%m-%d%H:%M")
        tags = request.form.get('tags')

        topic = Topic(name=name, description=description, dateTime=dateTime, tags=tags)
        db.session.add(topic)
        db.session.commit()

        return redirect(url_for('display_all'))

    return render_template("startquiz.html")

@app.route('/topics/<int:topic_id>' , methods = ['GET', 'POST'])
def description(topic_id):
    if request.method == 'POST':
        name = request.form.get('question')
        option1 = request.form.get('option-1')
        option2 = request.form.get('option-2')
        option3 = request.form.get('option-3')
        option4 = request.form.get('option-4')
        correct_answer = request.form.get('correct-answer')

        question = Question(
            name = name,
            topic_id = topic_id,
            option1 = option1,
            option2 = option2,
            option3 = option3,
            option4 = option4,
            correct_answer = correct_answer
        )

        db.session.add(question)
        db.session.commit()

        return redirect(url_for('review', topic_id=topic_id))

    topic = Topic.query.get(topic_id)
    return render_template("description.html", topic=topic)

@socketio.on('update_question')
def update_question_status(question_data):
    question = Question.query.get(question_data['id'])
    question.status = question_data['status']
    db.session.add(question)
    db.session.commit()
    emit('question_updated')

@app.route('/quiz/<int:topic_id>')
def gen_quiz(topic_id):
    
    hosted_by = request.args.get('hosted_by')
    duration = request.args.get('duration')
    max_marks = request.args.get('max_marks')

    topic = Topic.query.get(topic_id)
    questions = Question.query.filter_by(topic_id=topic_id, status=0)
    return render_template("quiz.html", questions=questions, topic=topic,
                        hosted_by=hosted_by, duration=duration, max_marks=max_marks )

@app.route('/create')
def drop_all():
    db.drop_all()
    db.create_all()
    return redirect(url_for('startquiz'))

@app.route('/drop')
def create_all():
    db.drop_all()
    return redirect(url_for('startquiz'))

if __name__ == "__main__":
    socketio.run(app)

# @app.route('/contact', methods = ['GET', 'POST'])
# def contact():
#    form = ContactForm()
   
#    if request.method == 'POST':
#       if form.validate() == False:
#          flash('All fields are required.')
#          return render_template('contact.html', form = form)
#       else:
#          return render_template('success.html')
#       elif request.method == 'GET':
#          return render_template('contact.html', form = form)
