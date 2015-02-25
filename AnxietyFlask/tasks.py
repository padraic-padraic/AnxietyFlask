from AnxietyFlask import app, anxieties, insert_reply, TotalFailure
from AnxietyFlask.mailgun import InMail, OutMail
from AnxietyFlask.models import Account
from flask import url_for
from celery import Celery, Task
from requests.exceptions import HTTPError

celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
TaskBase = Task
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
            insert_reply(user.id, message.body)

@celery.task(name='tasks.send_mail')
def send_mail():
    status = anxieties()
    if isinstance(status, HTTPError):
        raise TotalFailure(404)
    else:
        return status

@celery.task(name='tasks.send_activation')
def send_activation(account):
    body = "Hello, " + account.name.split(' ')[0] + ", <br>"
    body += "You've asked us to fill up an Anxiety Flask for you. <br> To confirm that, click"
    body += url_for('activate') + "?uuid=" + account.uid + "'> this link.</a> <br>"
    body += "Don't worry: every email will have a link to deactivate or delete your account in one click.<br>"
    body += "Best wishes, <br>"
    body += "Your anxiety."
    OutMail(to=account.email, text=body, html=body, subject="Open up your Anxiety Flask").send()
