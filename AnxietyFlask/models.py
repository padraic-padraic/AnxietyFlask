from AnxietyFlask.anxiety_bot import subject, compose
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime.now, timedelta
from random import choice

db = SQLAlchemy()

class Account(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(40))
    email = db.Column(db.String(120))
    reply = db.relationship('Reply', uselist=False, backref='Account',
                            lazy='dynamic')
    anxieties = db.relationship('Anxiety', backref='Account', lazy='dynamic')
    active = db.Column(db.Boolean)

    def include_reply(self):
        if now() - self.reply.last_included > timedelta(days=2):
            self.reply.last_included = now()
            return self.reply.reply
        else:
            return None

    def choose_anxiety(self):
        return choice(self.anxieties).anxiety

    @propery
    def email(self):
        return subject(), compose(self.name, self.choose_anxiety(), self.include_reply())

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
