FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./webapp /app

RUN pip install -r /app/requirements.txt
