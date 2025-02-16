FROM python:3.9-slim-bullseye

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

#RUN flask --app manage db upgrade

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "manage:app"]