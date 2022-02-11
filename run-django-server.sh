#!/usr/bin/env bash

source /etc/django_params
poetry run python manage.py runserver 0.0.0.0:8000
