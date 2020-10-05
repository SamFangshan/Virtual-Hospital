FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY virtual_hospital ./virtual_hospital
COPY .flaskenv ./
COPY wsgi.py ./
COPY entrypoint.sh ./

RUN apt-get update
RUN apt-get -y install cron
RUN apt-get -y install libpq-dev
RUN pip install -r requirements.txt --quiet

RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]
