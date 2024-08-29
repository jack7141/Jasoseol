FROM python:3.10

ADD ./requirements.txt /webapp/server/requirements.txt

RUN apt-get update \
    && mkdir -p /webapp/server \
    && pip install pip --upgrade \
    && pip install -r /webapp/server/requirements.txt

ADD . /webapp/server
WORKDIR /webapp/server

ENV RUNNING_ENV="local"

RUN mv ./conf/run.sh / \
    && chmod 755 /run.sh

EXPOSE 8000

CMD ["/run.sh"]
