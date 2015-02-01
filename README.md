# Anxiety Flask
### Copying people is how you learn!

## What?
This is an implementation of Paul Ford's [Anxiety Box](https://github.com/ftrain/anxietybox), but written in Flask instead.

## Why?
Because I'm new to Flask and wanted to mess around. Specifically, I wanted to practice with SQLAlchemy. This is also the largest little website project I've worked on by myself.

## How?
Once you've pointed it at a sqlite database and entered your mailgun details, you can mess around by simply doing
```pip install -r requirements.txt
   python AnxietyFlask/AnxietyFlask/runserver.py
```
And it will be available on localhost:8000.

There's also an install script coming that'll do some of the legwork for you.