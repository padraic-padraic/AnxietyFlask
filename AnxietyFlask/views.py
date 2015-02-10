from AnxietyFlask import app
from flask import render_template
from flask_wtf import Form
from wtforms import validators, StringField

class SignupForm(Form):
	pass

@app.route('/', methods=['GET'])
def root():
	return render_template('main_page.html')
