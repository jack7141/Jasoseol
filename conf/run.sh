#!/bin/bash

python manage.py migrate
python manage.py collectstatic --noinput

gunicorn --workers 3 --bind 0.0.0.0:8000 api_backend.asgi:application -k uvicorn.workers.UvicornWorker

