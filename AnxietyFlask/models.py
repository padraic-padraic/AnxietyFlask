from AnxietyFlask import AFException
from AnxietyFlask.anxiety_bot import subject, compose, process
from AnxietyFlask.tasks import send_activation
from datetime import datetime, timedelta
from flask.ext.sqlalchemy import SQLAlchemy
from random import choice
from uuid import uuid4


db = SQLAlchemy()

class Account(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(40))
    email = db.Column(db.String(120))
    reply = db.relationship('Reply', uselist=False, backref='Account')
    anxieties = db.relationship('Anxiety', backref='Account', lazy='dynamic')
    active = db.Column(db.Boolean)

    def include_reply(self):
        if self.reply is not None:
            if datetime.now() - self.reply.last_included > timedelta(days=2):
                self.reply.last_included = datetime.now()
                return self.reply.reply
        return None

    def choose_anxiety(self):
        return choice(self.anxieties.all()).anxiety

    @property
    def mail(self):
        return subject(), compose(self.uid, self.name, self.choose_anxiety(), self.include_reply())

    @classmethod
    def create_account(cls, _name, _email, _anxieties):
        new_account = cls(name=_name, email=_email, uid=uuid4().hex, active=False)
        db.session.add(new_account)
        db.session.commit()
        for anxiety in _anxieties:
            anxiety = process(anxiety)
            db.session.add(Anxiety(account_id=new_account.id, anxiety=anxiety))
            db.session.flush()
        db.session.commit()
        send_activation.delay(new_account)

    @classmethod
    def change_status(cls, status, email = None, uuid=None):
        if not any((uuid, email)):
            raise AFException(400, 'No account information provided')
        if email:
            account = cls.query.filter_by(email=email).first()
        else:
            account = cls.get_by_id(uuid)
        if account is None:
            raise AFException(404, 'No account found with that email address.')
        if account.active != status:
            account.active = status
            db.session.commit()
        return account

    @classmethod
    def delete(cls, email = None, uuid=None):
        if not any((uuid, email)):
            raise AFException(400, 'No account information provided')
        if email:
            account = cls.query.filter_by(email=email).first()
        else:
            account = cls.get_by_id(uuid)
        if account is None:
            raise AFException(404, 'No account found with that email address.')
        name = account.name.split(' ')[0]
        db.session.delete(account)
        db.session.commit()
        return name

    @classmethod
    def get_by_id(cls, _id):
        if isinstance(_id, int):
            return cls.query.filter_by(id=_id).first()
        else:
            return cls.query.filter_by(uid=_id).first()

class Anxiety(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    anxiety = db.Column(db.Text)
    # last_accessed = db.Column(db.DateTime)

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    reply = db.Column(db.Text)
    time = db.Column(db.DateTime)
    last_included = db.Column(db.DateTime)
