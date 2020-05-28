FROM python:3.7

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

CMD rm -rf /code/pachatary/staticfiles/* && python manage.py collectstatic --no-input && gunicorn --bind 0.0.0.0:$PORT pachatary.wsgi
