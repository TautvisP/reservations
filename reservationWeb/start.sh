#!/bin/bash

echo "Waiting for database..."
sleep 5  # Give the database a moment to be fully ready

echo "Running migrations..."
python manage.py migrate

if [ "$CREATE_SUPERUSER" = "yes" ]; then
  echo "Creating superuser..."
  # Use manage.py shell instead of direct Python to ensure settings are loaded
  python manage.py shell -c "
import os
from django.contrib.auth.models import User
username = os.environ.get('SUPERUSER_NAME', 'admin')
email = os.environ.get('SUPERUSER_EMAIL', '')
password = os.environ.get('SUPERUSER_PASSWORD')
if not User.objects.filter(username=username).exists() and password:
    User.objects.create_superuser(username, email, password)
    print('Superuser created successfully')
else:
    print('Superuser creation skipped')
"
fi

echo "Starting Gunicorn..."
gunicorn --bind 0.0.0.0:8000 reservationWeb.wsgi:application