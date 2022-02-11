#!/usr/bin/env bash

source /etc/django_params
poetry run uwsgi --socket /run/uwsgi/fymserver.sock --module fymserver.wsgi
