"""Flask implementation of @ftrain 's Anxiety Box project.
Mostly done as a personal exercise to build a bigger app in Flask
and learn SQLAlchemy/Sending mail"""

from AnxietyFlask.anxiety_bot import process
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

@app.errorhandler(400)
def bad_request(e):
    err = TotalFailure(400)
    return render_template('full_page.html', purpose='error', code=err.value, explanation=err.explanation)

@app.errorhandler(500)
def sever_error(e):
    err = TotalFailure(500)
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

from AnxietyFlask.tasks import send_activation

def create_account(_name, _email, _anxieties):
    with app.app_context():
        new_account = Account(name=_name, email=_email, uid=uuid4().hex, active=False)
        db.session.add(new_account)
        db.session.commit()
        for anxiety in _anxieties:
            anxiety = process(anxiety)
            db.session.add(Anxiety(account_id=new_account.id, anxiety=anxiety))
            db.session.flush()
        db.session.commit()
        send_activation(new_account)

def change_status(status, email = None, uuid=None):
    if not any((uuid, email)):
        raise TotalFailure(400, 'No account information provided')
    with app.app_context():
        if email: 
            account = Account.query.filter_by(email=email).first()
        else:
            account = Account.query.filter_by(uid=uuid).first()
        if account is None:
            raise TotalFailure(404, 'No account found with that email address.')
        if account.active != status:
            account.active = status
            db.session.commit()
        return account.id

@app.route('/activate', methods=['GET', 'POST'])
def activate():
    if request.method == 'POST':
        _id = change_status(True, email=request.form['email'])
    elif 'uuid' in request.args:
        _id = change_status(True, uuid=request.args.get('uuid'))
    else:
        return render_template('full_page.html', purpose='activate', form=True)
    account = Account.query.filter_by(id=_id).first()
    return render_template('full_page.html', purpose='activate', name=account.name.split(' ')[0])


@app.route('/deactivate', methods=['GET', 'POST'])
def deactivate():
    if request.method == 'POST':
        _id = change_status(False, email=request.form['email'])
    elif 'uuid' in request.args:
        _id = change_status(False, uuid=request.args.get('uuid'))
    else:
        return render_template('full_page.html', purpose='deactivate', form=True)
    account = Account.query.filter_by(id=_id).first()
    return render_template('full_page.html', purpose='deactivate', name=account.name.split(' ')[0])

def delete_account(email = None, uuid=None):
    if not any((uuid, email)):
        raise TotalFailure(400, 'No account information provided')
    with app.app_context():
        if email:
            account = Account.query.filter_by(email=email).first()
        else:
            account = Account.query.filter_by(uid=uuid).first()
        if account is None:
            raise TotalFailure(404, 'No account found with that email address.')
        name = account.name.split(' ')[0]
        db.session.delete(account)
        db.session.commit()
        return name

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        name = delete_account(email=request.form['email'])
    elif 'uuid' in request.args:
        name = delete_account(uuid=request.args.get('uuid'))
    else:
        return render_template('full_page.html', purpose='delete', form=True)
    return render_template('full_page.html', purpose='delete', name=name)

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
