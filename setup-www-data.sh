#!/usr/bin/env bash

curl -sSL https://install.python-poetry.org | sudo POETRY_HOME=/etc/poetry python3 -

sudo ln -s /etc/poetry/bin/poetry /usr/local/bin/poetry

sudo -u www-data poetry install

sudo -u www-data bash -c ". /etc/django_params && poetry run ./manage.py migrate && poetry run ./manage.py collectstatic"
