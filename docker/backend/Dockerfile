FROM ubuntu

RUN apt-get update && apt-get install -y tar git curl wget build-essential python-software-properties\
	python python-dev python-distribute python-pip \
	libmysqlclient-dev libjpeg-dev libpng3 libpcre3 libpcre3-dev

ADD repo-key /
RUN \
  chmod 600 /repo-key && \
  echo "IdentityFile /repo-key" >> /etc/ssh/ssh_config && \
  echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

RUN pip install uwsgi flask pymysql python-dateutil SQLAlchemy flask-sqlalchemy flask-security flask-restless flask-cache flask-babelex flask-mail flask-debugtoolbar MySQL-Python redis celery alembic Pillow termcolor alchemyjsonschema flask-admin

# Run git clone https://github.com/mattupstate/flask-jwt && cd flask-jwt && pip install .
# Run git clone https://github.com/mrjoes/flask-admin && cd flask-admin && pip install .

RUN cp /usr/share/zoneinfo/Asia/Hong_Kong /etc/localtime

RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:git-core/ppa -y && apt-get update && apt-get -y upgrade

RUN git --version

ADD ./run.sh /run.sh
ADD ./uwsgi.ini /uwsgi.ini

RUN chmod 755 /*.sh

CMD /run.sh
