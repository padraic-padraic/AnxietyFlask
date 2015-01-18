"""Flask implementation of @ftrain 's Anxiety Box project.
Mostly done as a personal exercise to build a bigger app in Flask
and learn SQLAlchemy/Sending mail"""

from AnxietyFlask.models import Account, Anxiety, Reply, db
from flask import Flask
from flask import request
from random import choice
from uuid import uuid4

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///tmp/test.db'
db.init_app(app)

##Helpful Functions
def get_account_id(_uuid):
    return Account.query.filter_by(uid=_uuid).first().account_id

def get_account(_id):
    if isinstance(_id, int):
        return Account.get(_id)
    elif isinstance(_id, str):
        return Account.query.filter_by(uid=_id).first()
    else:
        raise NotFoundException('No Account with that ID found')

def get_anxiety(_a_id):
    return choice(Anxiety.query.filter_by(account_id=_a_id))

def get_reply(_a_id):
    return Reply.query.filter_by(account_id=_a_id).first()

def insert_reply(_a_id, _reply):
    _r = get_reply(_a_id)
    if _r is None:
        _r = Reply(account_id=_aid, reply=_reply)
        db.session.add(_r)
    else:
        _r.reply = _reply
    db.session.commit()

def insert_anxiety(_a_id, _anxiety):
    db.session.add(Anxiety(account_id=_a_id, anxiety=_anxiety))
    db.session.flush()

## Endpoints
def create_account(_name, _email, anxieties):
    new_account = Account(name=_name, email=_email, uid=uuid4.hex, active=False)
    db.session.add(new_account)
    db.session.flush()
    for anxiety in anxieties:
        insert_anxiety(new_account.id, _anxiety)
    db.session.commit()
    
def activate(uuid):
    pass

def deactivate(uuid):
    pass
