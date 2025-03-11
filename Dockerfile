FROM python:3.9-slim-bullseye

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000