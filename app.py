import flask
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_socketio import SocketIO
from flask_socketio import emit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import Topic, Question, User
from config import app, db
from flask_login import LoginManager
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from functions import calcSimilarity
from sqlalchemy import or_

login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app)

login_manager.login_view = "register"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/search')
def search_topics():
    q = request.args.get('q')
    topics = Topic.query.filter(or_(Topic.name.like('%'+q+'%'), Topic.tags.like('%'+q+'%'), Topic.description.like('%'+q+'%'))).all()
    return render_template("all.html", topics=topics, all=True)

@app.route('/topics')
def display_all():
    topics = Topic.query.all()
    return render_template("all.html", topics=topics, all=True)

@app.route('/my-topics')
def display_my():
    topics = Topic.query.filter_by(user_id=current_user.id).all()
    return render_template("all.html", topics=topics, all=False)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    
    global next
    if request.method == 'POST':

        if request.form.get('submit') == "login":
            user = User.query.filter_by(username=request.form.get('username')).first()
            if user is None or not user.check_password(request.form.get('password')):
                flash('Invalid username or password')
                return redirect(url_for('register'))
            
            login_user(user, remember=request.form.get('remember'))

        elif request.form.get('submit') == "register":
            name = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            user = User(username=name, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=request.form.get('remember'))            

        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        # if not is_safe_url(next):
        #     return flask.abort(400)

        return redirect(next or url_for('display_all'))
    
    else:
        next = request.args.get('next')
    
    print(next)
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/review/<int:topic_id>')
@login_required
def review(topic_id):
    questions = Question.query.filter_by(topic_id=topic_id).all()
    return render_template("review.html", questions=questions, topic_id=topic_id)

@app.route('/')
def landing():
    topics = Topic.query.all()[:4]
    return render_template("landing.html", topics=topics)

@app.route('/startquiz', methods = ['GET', 'POST'])
@login_required
def startquiz():
    if request.method == 'POST':
        name = request.form.get('name')
        user_id = current_user.id
        description = request.form.get('description')
        date = request.form.get('date')
        time = request.form.get('time')
        dateTime = datetime.strptime(date+time, "%Y-%m-%d%H:%M")
        tags = request.form.get('tags')

        topic = Topic(name=name, user_id=user_id, description=description, dateTime=dateTime, tags=tags)
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

        questions = Question.query.filter_by(topic_id=topic_id)
        for question in questions:
            sim = calcSimilarity(name, question.name)
            print(sim)
            if(sim >= 0.5):
                flash("A similar question has already been submitted! <br>Try submitting a different question :)")
                return redirect(url_for('description', topic_id=topic_id))

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
@login_required
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
    app.run(debug = True, port = 5000)
    socketio.run(app)