FROM python:3.10

ADD ./requirements.txt /webapp/server/requirements.txt

RUN apt-get update \
    && mkdir -p /webapp/server \
    && pip install pip --upgrade \
    && pip install -r /webapp/server/requirements.txt

ADD . /webapp/server
WORKDIR /webapp/server

ENV NGINX_SET_REAL_IP_FROM="172.18.0.0/16"\
    UWSGI_SOCKET="/webapp/uwsgi/webapp.sock"\
    UWSGI_PID="/webapp/uwsgi/webapp.pid"\
    UWSGI_CHDIR="/webapp/server"\
    UWSGI_MODULE="api_backend.wsgi"\
    RUNNING_ENV="base"

RUN mv ./conf/run.sh / \
    && chmod 755 /run.sh

EXPOSE 8000

CMD ["/run.sh"]
