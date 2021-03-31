#!/usr/bin/env sh

cd app || echo "CD Fail"
python manage.py collectstatic --noinput
python manage.py migrate
