web: gunicorn smartcache.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A smartcache worker --loglevel=info
beat: celery -A smartcache beat --loglevel=info