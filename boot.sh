#!/bin/bash
while true; do
    flask --app manage db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done
exec gunicorn --bind :8000 manage:app