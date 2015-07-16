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

class AFException(Exception):
    """Wrapper around HTTP exceptions used for my error pages."""
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

BACKGROUND_IMAGES={'error':['http://xkcd.com/961', 'XKCD by Randall Monroe'],
                   'activate':['http://blog.newspaperclub.com/2012/11/02/newspaper-animated-gifs/', 'The Newspaper Club'],
                   'deactivate':['https://www.youtube.com/watch?v=jJaft0a5VXc','Youtube, Syndey Analogue TV Shutdown'],
                   'delete':['http://d36wcktvpv3t5z.cloudfront.net/images/3c48b6db-6cd1-4db4-bc71-7a437fdac7a3.gif','Office Space, creator unattributeable']}

@app.errorhandler(AFException)
def error(err):
    return render_template('full_page.html', purpose='error', source=BACKGROUND_IMAGES['error'], code=err.value, explanation=err.explanation, info=err.info)

@app.errorhandler(404)
def not_found(e):
    err = AFException(404)
    return render_template('full_page.html', purpose='error', source=BACKGROUND_IMAGES['error'], code=err.value, explanation=err.explanation)

@app.errorhandler(400)
def bad_request(e):
    err = AFException(400)
    return render_template('full_page.html', purpose='error', source=BACKGROUND_IMAGES['error'], code=err.value, explanation=err.explanation)

@app.errorhandler(500)
def sever_error(e):
    err = AFException(500)
    return render_template('full_page.html', purpose='error', source=BACKGROUND_IMAGES['error'], code=err.value, explanation=err.explanation)
#CSRF Token Snippet from http://flask.pocoo.org/snippets/3/
@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = some_random_string()
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

##Routes##

@app.route('/activate', methods=['GET', 'POST'])
def activate():
    if request.method == 'POST':
        account = Account.change_status(True, email=request.form['email'])
    elif 'uuid' in request.args:
        account = Account.change_status(True, uuid=request.args.get('uuid'))
    else:
        return render_template('full_page.html', purpose='activate', source=BACKGROUND_IMAGES['activate'], form=True)
    return render_template('full_page.html', purpose='activate', source=BACKGROUND_IMAGES['activate'], name=account.name.split(' ')[0])

@app.route('/deactivate', methods=['GET', 'POST'])
def deactivate():
    if request.method == 'POST':
        account = Account.change_status(False, email=request.form['email'])
    elif 'uuid' in request.args:
        account = Account.change_status(False, uuid=request.args.get('uuid'))
    else:
        return render_template('full_page.html', purpose='deactivate', source=BACKGROUND_IMAGES['deactivate'], form=True)
    return render_template('full_page.html', purpose='deactivate', source=BACKGROUND_IMAGES['deactivate'], name=account.name.split(' ')[0])

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        name = Account.delete(email=request.form['email'])
    elif 'uuid' in request.args:
        name = Account.delete(uuid=request.args.get('uuid'))
    else:
        return render_template('full_page.html', purpose='delete', source=BACKGROUND_IMAGES['delete'], form=True)
    return render_template('full_page.html', purpose='delete', source=BACKGROUND_IMAGES['delete'], name=name)

@app.route('/send', methods=['GET'])
def send():
#I created this to manually review bouncing emails... How?
    pass
## Views
@app.route('/', methods=['GET'])
def root():
    return render_template('main_page.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        Account.create_account(request.form['name'], request.form['email'], request.form['anxieties'].split(', '))
        return render_template('full_page.html', purpose='welcome', name=request.form['name'].split(' ')[0])
    else:
        raise AFException(400, "You're not supposed to be here. Not like this.")
