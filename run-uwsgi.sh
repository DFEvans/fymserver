#!/usr/bin/env bash

source /etc/django_params
poetry run uwsgi --socket /tmp/fymserver.sock --module fymserver.wsgi
