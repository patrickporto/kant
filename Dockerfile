FROM python:3.5

WORKDIR /usr/src/app

COPY . .

CMD python setup.py test
