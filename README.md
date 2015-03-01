# Anxiety Flask
### Copying people is how you learn!

## What?
This is an implementation of Paul Ford's [Anxiety Box](https://github.com/ftrain/anxietybox), but written in Flask instead.

## Why?
Because I'm new to Flask and wanted to mess around. Specifically, I wanted to practice with SQLAlchemy. This is also the largest little website project I've worked on by myself.

## How?
Anxiety Flask is written in Python 2.7. Outside of python packages, you'll need sqlite and redis installed.

Once you've set the database URI and entered your mailgun details, you can mess around by simply doing
```
   pip install -r requirements.txt
   screen -d -m redis-server
   screen -d -m celery -A AnxietyFlask.tasks.celery worker -B
   python AnxietyFlask/runserver.py
```
And it will be available on localhost:5000.
