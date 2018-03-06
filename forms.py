from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField

from wtforms import validators, ValidationError

class StartQuizForm(Form):
   name = TextField("topic",[validators.Required("Please enter topic name")])
   description = TextAreaField("description")
      
   submit = SubmitField("send")