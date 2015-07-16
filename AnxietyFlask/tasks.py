from AnxietyFlask import make_app
from AnxietyFlask.emails import *
from AnxietyFlask.mailgun import InMail, OutMail
from AnxietyFlask.models import db, Account, Reply
from flask import url_for
from celery import Celery
from datetime import timedelta
from datetime.datetime import now
from requests.exceptions import HTTPError
from random import random, shuffle

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

class SendingException(HTTPError):
    def __init__(self, _e, _user):
        self.user = user
        super(SendingException, self).__init__(response=_e.response, request=_e.request)

    def __str__(self):
        return FAILURE_PLAIN.format(email=self.user.email, code=self.response.status_code, uid=self.user.uid)

    def html(self):
        return FAILURE_HTML.format(email=self.user.email, code=self.response.status_code, uid=self.user.uid)

@celery.task(name='tasks.process')
def process_mail(message):
        user = Account.query.filter_by(email=message.parameters['from']).first()
        if user is None:
            ## Nothing more to do here; the email is likely spam etc
            return None
        else:
            reply = user.reply.get()
            if reply is None:
                reply = Reply(account_id=user.id, reply=message.parameters['body-html'])
            else:
                reply.reply = message.parameters['body-html']
            db.session.commit()

@celery.task(name='tasks.get_mail', ignore_result=True)
def get_mail():
    mail = InMail().get_messages()
    for message in mail:
        process.delay(message)

@celery.task(name='tasks.check_errors')
def notify_sending_error(results):
    failed = [res for res in results if res.status != 'SUCCESS']
    if failed:
        failed_plain = [str(x.get()) for x in failed]
        failed_html = [x.get().html() for x in failed]
    plain_text = ADMIN_PLAIN.format(app.config['ADMIN'], failed_plain)
    html = ADMIN_HTML.format(app.config['ADMIN'], failed_html)
    OutMail(subject='Sending Failed', body=plain_text, html=html, to=app.config['ADMIN_EMAIL'])

@celery.task(name='tasks.send_mail')
def send_mail():
    actives = Account.query.filter_by(active = True).all()
    shuffle(actives)
    results = [your_anxiety.delay(countdown=random()*3600, retry=True) for user in users]
    check_errors.delay(results, eta=now()+timedelta(minutes=120))

@celery.task(name='tasks.your_anxiety')
def anxiety_nudge(user):
    _subject, emails = user.mail
    plain_text, html = emails
    try:
        OutMail(subject=_subject, body=plain_text, html=html, to=user.email).send()
    except HTTPError as _e:
        raise SendingException(_e, user)

@celery.task(name='tasks.send_activation')
def send_activation(account):
    plain = ACTIVATION_TEMPLATE.format(account.name.split(' ')[0], domain=app.config['DOMAIN'], uid=account.uid)
    html = ACTIVATION_HTML.format(account.name.split(' ')[0], domain=app.config['DOMAIN'], uid=account.uid)
    OutMail(to=account.email, text=plain, html=html, subject="Confirm your account").send()
