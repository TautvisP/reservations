#!/bin/bash

echo "Waiting for database..."
sleep 5  # Give the database a moment to be fully ready

echo "Running migrations..."
python manage.py migrate

echo "Starting Gunicorn..."
gunicorn --bind 0.0.0.0:8000 reservationWeb.wsgi:application