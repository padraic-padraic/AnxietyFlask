"""Flask implementation of @ftrain 's Anxiety Box project.
Mostly done as a personal exercise to build a bigger app in Flask
and learn SQLAlchemy/Sending mail"""

from AnxietyFlask.config import Config
from AnxietyFlask.mailgun import InMail, OutMail
from AnxietyFlask.models import db, Account, Anxiety, Reply
from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from random import choice
from requests.exceptions import HTTPError
from uuid import uuid4

class TotalFailure(Exception):
    explanations = {400: 'Something is wrong with the request.',
                         404: 'This doesn\'t, and perhaps shall never, exist.',
                         500: 'Something went very wrong. On our end. We\'re on it.'}
    def __init__(self, value, *args):
        self.value = value
        self.explanation = self.explanations[value]
        if args:
            self.info = args[0]
    def __str__(self):
        return repr((self.value, self.explanation))
def make_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    Bootstrap(app)
    with app.app_context():
        db.create_all()
    return app

app = make_app()

@app.errorhandler(TotalFailure)
def error(err):
    return render_template('full_page.html', purpose='error', code=err.value, explanation=err.explanation, info=err.info)
@app.errorhandler(404)
def not_found(e):
    err = TotalFailure(404)
    return render_template('full_page.html', purpose='error', code=err.value, explanation=err.explanation)

##Helpful Functions
def get_account_id(_uuid):
    with app.app_context():
        return Account.query.filter_by(uid=_uuid).first().account_id

def get_account(_id):
    with app.app_context():
        if isinstance(_id, int):
            return Account.query.filter_by(id=_id).first()
        else:
            return Account.query.filter_by(uid=_id).first()
        
def insert_anxiety(_a_id, _anxiety):
    with app.app_context():
        db.session.add(Anxiety(account_id=_a_id, anxiety=_anxiety))
        db.session.flush()

from AnxietyFlask.tasks import send_activation

def create_account(_name, _email, _anxieties):
    with app.app_context():
        new_account = Account(name=_name, email=_email, uid=uuid4().hex, active=False)
        db.session.add(new_account)
        db.session.commit()
        for anxiety in _anxieties:
            insert_anxiety(new_account.id, anxiety)
        db.session.commit()
        send_activation(new_account)

def change_status(account, status):
    with app.app_context():
        if account.active != status:
            account.active = status
        db.session.commit()

@app.route('/activate', methods=['GET', 'POST'])
def activate():
    if request.method == 'POST':
        account = Account.query.filter_by(email=request.args.get('email'))
        change_status(account, True)
        return render_template('full_page.html', purpose='activate', name=account.name.split(' ')[0])
    if 'uuid' in request.args:
        account = Account.query.filter_by(uid = request.args.get('uuid'))
        change_status(account, True)
        return render_template('full_page.html', purpose='activate', name=account.name.split(' ')[0])
    else:
        return render_template('full_page.html', purpose='activate', form=True)

@app.route('/deactivate', methods=['GET', 'POST'])
def deactivate():
    if request.method == 'POST':
        account = Account.query.filter_by(email=request.args.get('email'))
        change_status(account, True)
        return render_template('full_page.html', purpose='deactivate', name=account.name.split(' ')[0])
    if 'uuid' in request.args:
        account = Account.query.filter_by(uid = request.args.get('uuid'))
        change_status(account, True)
        return render_template('full_page.html', purpose='deactivate', name=account.name.split(' ')[0])
    else:
        return render_template('full_page.html', purpose='deactivate', form=True)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        account = Account.query.filter_by(email=request.args.get('email'))
        db.delete(account)
        db.session.commit()
        return render_template('full_page.html', purpose='delete', name=account.name.split(' ')[0])
    if 'uuid' in request.args:
        account = Account.query.filter_by(uid = request.args.get('uuid'))
        db.delete(account)
        db.session.commit()
        return render_template('full_page.html', purpose='delete', name=account.name.split(' ')[0])
    else:
        return render_template('full_page.html', purpose='delete', form=True)

@app.route('/send', methods=['GET'])
def send():
    pass
## Views
@app.route('/', methods=['GET'])
def root():
    return render_template('main_page.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        create_account(request.form['name'], request.form['email'], request.form['anxieties'].split(', '))
        return render_template('full_page.html', purpose='welcome', name=request.form['name'].split(' ')[0])
    else:
        raise TotalFailure(400, "You're not supposed to be here. Not like this.")
