flask db upgrade
gunicorn -b :8000 --access-logfile - --error-logfile - manage:app