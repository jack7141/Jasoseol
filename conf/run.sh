#!/bin/bash

python manage.py migrate

exec gunicorn api_backend.asgi:application -k uvicorn.workers.UvicornWorker --workers=4 --bind 0.0.0.0:8000
