from flask.ext.sqlalchemy import SQLAlchemy
from random import choice

db = SQLAlchemy()

class Account(db.Model):
    id = db.Column(db.Integer)
    uid = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(40))
    email = db.Column(db.String(120))
    reply = db.relationship('Reply', uselist=False, backref='Account',
                            lazy='dynamic')
    anxieties = db.relationship('Anxiety', backref='Account', lazy='dynamic')
    active = db.Column(db.Boolean)

    def choose_anxiety(self):
        return choice(self.anxieties).anxiety

class Anxiety(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    anxiety = db.Column(db.Text)
    # last_accessed = db.Column(db.DateTime)

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    reply = db.Column(db.Text)
    last_included = db.Column(db.DateTime)
