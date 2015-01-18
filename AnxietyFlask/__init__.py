"""Flask implementation of @ftrain 's Anxiety Box project.
Mostly done as a personal exercise to build a bigger app in Flask
and learn SQLAlchemy/Sending mail"""

from AnxietyFlask.database import db_session
from flask import Flask
from flask import request

app = Flask(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
