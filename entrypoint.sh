#!/bin/sh
# echo 'Running collecstatic...'
# python3 manage.py collectstatic --no-input --settings=sistema.settings

# python manage.py makemigrations --settings=sistema.settings
# echo 'Applying migrations...'   

# python manage.py migrate --settings=sistema.settings

# echo 'Running server...'
# gunicorn --env DJANGO_SETTINGS_MODULE=sistema.settings sistema.wsgi:application --bind 0.0.0.0:8080


# gunicorn --workers 4 --bind 0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=sistema.settings sistema.wsgi:application


#!/bin/sh
echo 'Running collectstatic...'
python3 manage.py collectstatic --no-input --settings=sistema.settings

echo 'Making migrations...'
python manage.py makemigrations --settings=sistema.settings

echo 'Applying migrations...'
python manage.py migrate --settings=sistema.settings

echo 'Running server with Gunicorn and gevent...'
gunicorn -k gevent --workers 4 --env DJANGO_SETTINGS_MODULE=sistema.settings sistema.wsgi:application --bind 0.0.0.0:8080
