"""Flask implementation of @ftrain 's Anxiety Box project.
Mostly done as a personal exercise to build a bigger app in Flask
and learn SQLAlchemy/Sending mail"""

from AnxietyFlask.mailgun import InMail, OutMail
from AnxietyFlask.models import Account, Anxiety, Reply, db
from celery import Celery
from flask import Flask
from flask import request
from random import choice
from uuid import uuid4

app = None

def make_app():
    ## Initialise and set up the application
    app = Flask(__name__)
    #Change this
    app.config.from_object(AnxietyFlask.config.Config)
    db.init_app(app)
    mailer.init_app(app)
    return app

def make_celery_app(app=None):
    if app is None:
        app = make_app()
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

##Helpful Functions
def get_account_id(_uuid):
    return Account.query.filter_by(uid=_uuid).first().account_id

def get_account(_id):
    if isinstance(_id, int):
        return Account.get_or_404(_id)
    elif isinstance(_id, str):
        return Account.query.filter_by(uid=_id).first_or_404()
    else:
        #raise  #What is that in flask?

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
    account = get_account(uuid)
    if account.active:
        return
    else:
        account.active = True
    db.session.commit()

def deactivate(uuid):
    account = get_account(uuid)
    if not account.active:
        return
    account.active = False
    db.session.commit()

def anxieties():
    active_accounts = Account.query.filter_by(active=True).all()
    send_mail(active_accounts)

## Views
