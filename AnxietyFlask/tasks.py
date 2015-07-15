from AnxietyFlask import make_app, AFException
from AnxietyFlask.emails import ACTIVATION_TEMPLATE, ACTIVATION_HTML
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

@celery.task(name='tasks.send_mail')
def send_mail():
    actives = Account.query.filter_by(active = True).all()
    failed_users = []
    for user in actives:
        _subject, emails = user.mail
        plain_text, html = emails
        try:
            OutMail(subject=_subject, body=plain_text, html=html, to=user.email).send()
        except HTTPError as _e:
            if _e.errno == 404:
                return _e
            failed_users.append((user, _e.errno))
    return failed_users


@celery.task(name='tasks.send_activation')
def send_activation(account):
    plain = ACTIVATION_TEMPLATE.format(account.name.split(' ')[0], domain=DOMAIN, uid=account.uid)
    html = ACTIVATION_HTML.format(account.name.split(' ')[0], domain=DOMAIN, uid=account.uid)
    OutMail(to=account.email, text=plain, html=html, subject="Confirm your account").send()
