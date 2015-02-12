from AnxietyFlask import app
from flask import render_template, redirect
from flask_wtf import Form, CsrfProtect
from wtforms import validators, StringField
from wtforms.fields.html5 import EmailField

csrf = CsrfProtect()

@csrf.error_handler
def csrf_error(reason):
	return render_template('csrf_error.html', reason=reason), 400

class SignupForm(Form):
	name = StringField('name', validators=[validators.InputRequired()])
	email = EmailField('email', validators=[validators.InputRequired(), validators.Email()])
	anxieties = StringField('anxieties', validators=[validators.InputRequired()])


@app.route('/', methods=['GET'])
def root():
	signup = SignupForm()
	if signup.validate_on_submit():
		return redirect('/welcome_aboard')
	return render_template('main_page.html', signup_form=signup)
