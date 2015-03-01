pip install -r requirements.txt
mv AnxietyFlask.conf /etc/apache2/sites-available
a2dissite 000-default.conf
a2ensite AnxietyFlask.conf
service apache2 restart
screen -d -m redis-server
screen -d -m celery -A AnxietyFlask.tasks.celery beat
screen -d -m celery -A AnxietyFlask.tasks.celery worker