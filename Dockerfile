FROM python:3.9-slim-bullseye

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY app app

RUN mkdir /var/logs/manga-reader

COPY migrations migrations
COPY manage.py config.py boot.sh ./
RUN chmod a+x boot.sh

EXPOSE 8000

ENTRYPOINT ["./boot.sh"]