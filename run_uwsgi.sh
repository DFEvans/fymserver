#!/usr/bin/env bash

poetry run uwsgi --http :8000 --module fymserver.wsgi
