#!/bin/bash
# Migration script to run on Cloud Run

python manage.py migrate
python manage.py createsuperuser --noinput --email admin@qglide.com --username admin || true

