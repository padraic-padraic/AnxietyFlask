"""Flask implementation of @ftrain 's Anxiety Box project.
Mostly done as a personal exercise to build a bigger app in Flask
and learn SQLAlchemy/Sending mail"""

from AnxietyFlask.mailgun import InMail, OutMail
from AnxietyFlask.models import Account, Anxiety, Reply, db
from AnxietyFlask.factory import make_app
from flask import request
from random import choice
from request.exceptions import HttpError
from uuid import uuid4

app = None
app = make_app()

##Helpful Functions
def get_account_id(_uuid):
    with app.app_context():
        return Account.query.filter_by(uid=_uuid).first().account_id

def get_account(_id):
    with app.app_context():
        if isinstance(_id, int):
            return Account.get_or_404(_id)
        elif isinstance(_id, str):
            return Account.query.filter_by(uid=_id).first_or_404()
        else:
            #raise  #What is that in flask?

def get_reply(_a_id):
    with app.app_context():
        return reply = Reply.query.filter_by(account_id=_a_id).first()

def anxieties():
    actives = Account.query.filter_by(active = True).all()
    failed_users = []
    for user in actives:
        _subject, _compose = user.email
        try:
            Outmail(subject=_subject, body=_compose, to=user.email).send()
        except HttpError as _e:
            if _e.errno == 404:
                return _e
            failed_users.append((user, _e.errno))
    return failed_users

## Endpoints
def insert_reply(_a_id, _reply):
    with app.app_context():
        _r = get_reply(_a_id)
        if _r is None:
            _r = Reply(account_id=_aid, reply=_reply)
            db.session.add(_r)
        else:
            _r.reply = _reply
        db.session.commit()

def insert_anxiety(_a_id, _anxiety):
    with app.app_context():
        db.session.add(Anxiety(account_id=_a_id, anxiety=_anxiety))
        db.session.flush()

def create_account(_name, _email, anxieties):
    with app.app_context():
        new_account = Account(name=_name, email=_email, uid=uuid4.hex, active=False)
        db.session.add(new_account)
        db.session.flush()
        for anxiety in anxieties:
            insert_anxiety(new_account.id, _anxiety)
        db.session.commit()
   
@app.route('/api/deactivate', methods=['GET'])
def activate():
    account = get_account(uuid)
    if account.active:
        return
    else:
        account.active = True
    db.session.commit()

@app.route('/api/activate', methods=['GET'])
def deactivate():
    account = get_account(request.args.get('uuid')
    if not account.active:
        return
    account.active = False
    db.session.commit()

@app.route('/api/send', methods=['GET'])
def send():
    pass

## Views
