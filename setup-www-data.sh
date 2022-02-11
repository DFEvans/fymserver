#!/usr/bin/env bash

set -eux

curl -sSL https://install.python-poetry.org | sudo POETRY_HOME=/etc/poetry python3 -

sudo ln -sf /etc/poetry/bin/poetry /usr/local/bin/poetry

export DJANGO_PARAMS_FILE="/etc/django_params.ini"

sudo -u www-data --preserve-env=DJANGO_PARAMS_FILE poetry config virtualenvs.path "/var/www/poetry/"
sudo -u www-data --preserve-env=DJANGO_PARAMS_FILE poetry install
sudo -u www-data --preserve-env=DJANGO_PARAMS_FILE poetry run ./manage.py migrate
sudo -u www-data --preserve-env=DJANGO_PARAMS_FILE poetry run ./manage.py collectstatic --noinput
