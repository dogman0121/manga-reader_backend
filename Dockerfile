FROM python:3.9-slim-bullseye

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

RUN chmod a+x boot.sh

EXPOSE 8000

CMD ["./boot.sh"]