"""Flask implementation of @ftrain 's Anxiety Box project.
Mostly done as a personal exercise to build a bigger app in Flask
and learn SQLAlchemy/Sending mail"""

from AnxietyFlask.mailgun import InMail, OutMail
from AnxietyFlask.models import Account, Anxiety, Reply, db
from AnxietyFlask.factory import make_app
from flask import request
from random import choice
from requests.exceptions import HTTPError
from uuid import uuid4

import AnxietyFlask.views

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
            raise Exception

def get_reply(_a_id):
    with app.app_context():
        return Reply.query.filter_by(account_id=_a_id).first()

def anxieties():
    actives = Account.query.filter_by(active = True).all()
    failed_users = []
    for user in actives:
        _subject, _compose = user.email
        try:
            OutMail(subject=_subject, body=_compose, to=user.email).send()
        except HttpError as _e:
            if _e.errno == 404:
                return _e
            failed_users.append((user, _e.errno))
    return failed_users

def insert_reply(_a_id, message):
    with app.app_context():
        reply = get_reply(_a_id)
        if reply is None:
            reply = Reply(account_id=_a_id, reply=message)
            db.session.add(reply)
        else:
            reply.reply = message
        db.session.commit()

def insert_anxiety(_a_id, _anxiety):
    with app.app_context():
        db.session.add(Anxiety(account_id=_a_id, anxiety=_anxiety))
        db.session.flush()

def create_account(_name, _email, _anxieties):
    with app.app_context():
        new_account = Account(name=_name, email=_email, uid=uuid4().hex, active=False)
        db.session.add(new_account)
        db.session.flush()
        for anxiety in _anxieties:
            insert_anxiety(new_account.id, anxiety)
        db.session.commit()
   
@app.route('/api/account_status', methods=['GET'])
def activate():
    account = get_account(request.args.get('uuid'))
    new_status = request.args.get('status')
    if account.active == new_status:
        return
    account.active = new_status
    db.session.commit()
    return True

@app.route('/api/send', methods=['GET'])
def send():
    pass
## Views
