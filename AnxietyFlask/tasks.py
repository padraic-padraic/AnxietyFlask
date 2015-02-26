from AnxietyFlask import make_app, TotalFailure
from AnxietyFlask.mailgun import InMail, OutMail
from AnxietyFlask.models import db, Account, Reply
from flask import url_for
from celery import Celery
from requests.exceptions import HTTPError

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

MANUAL_SEND_ENDPOINT = "http://path-to-site.com/api/send?uid="

@celery.task(name='tasks.error_mailer')
def error_mailer(failed_users):
    if len(failed_users) == 0:
        return True
    body = "Dear" + celery.conf.ADMIN + "<br> This is an email to let you know something went wrong (predictably).<br>"
    body += "For you, a great many things have gone wrong, but that's neither here nor there: I'm talking"
    body += "about the website. Here's a list. <br>"
    for failure, error in failed_users:
        body += "Account: " + failure.id + "<br>"
        body += "Error Code: " + error + "<br>"
        body += "To do something about it, click: " +  MANUAL_SEND_ENDPOINT + failure.uid
        body += "<br> <br>"
    body += 'Best wishes, <br> Your Anxiety'
    OutMail(to=celery.conf.ADMIN_MAIL, subject = "More things you did wrong", text=body, html=body).send()

@celery.task(name='tasks.get_mail')
def get_mail():
    mail = InMail().get_messages()
    for message in mail:
        user = Account.query.filter_by(email=message.parameters['from']).first()
        if user is None:
            continue #Need to do more here
        else:
            reply = Reply.query.filter_by(account_id=user.id).first()
            if reply is None:
                reply = Reply(account_id=user.id, reply=message.parameters['body-html'])
                db.session.add(reply)
            else:
                reply.reply = message.parameters['body-html']
            db.session.flush()
    db.session.commit()

@celery.task(name='tasks.send_mail')
def send_mail():
    actives = Account.query.filter_by(active = True).all()
    failed_users = []
    for user in actives:
        _subject, plain_text, html = user.mail
        try:
            OutMail(subject=_subject, body=plain_text, html=html, to=user.email).send()
        except HTTPError as _e:
            if _e.errno == 404:
                return _e
            failed_users.append((user, _e.errno))
        return failed_users


ACTIVATION_TEMPLATE = """
Dear {0},

You've asked us to fill up an Anxiety Flask for you. 

To confirm that, click this link:
anxietyflask.ddns.net/activate?uuid={1}

Don't worry. If it gets overwhelming, each email will have a link to deactivate or delete your account in one click. Or, you can do it any time at 
anxietyflask.ddns.net/deactivate
anxietyflask.ddns.net/delete

Sincerely, 
Your Anxiety
"""

ACTIVATION_HTML = """
Dear {0}, <br>
You've asked us to fill up an Anxiety Flask for you. <br>
To confirm that, click <a href="anxietyflask.ddns.net/activate?uuid={1}"> here</a>. <br>
Don't worry, if it gets overwhelming you can always <a href="anxietyflask.ddns.net/deactivate>deactivate</a> or <a href="anxietyflask.ddns.net/delete">delete</a> your account.<br>
Sincerely, <br> Your Anxiety
"""
@celery.task(name='tasks.send_activation')
def send_activation(account):
    plain = ACTIVATION_TEMPLATE.format(account.name.split(' ')[0], account.uid)
    html = ACTIVATION_HTML.format(account.name.split(' ')[0], account.uid)    
    OutMail(to=account.email, text=plain, html=html, subject="Confirm your account").send()
