
FROM chenzhao/gmission


#RUN git clone https://95d95a76fba2f34e86d9eb9ba6aaeae661734629@github.com/jimidata/GMission-Server.git && cd GMission-Server && git pull && git checkout docker-testing
# git clone breaks sometime

WORKDIR /GMission-Server/hkust-gmission

CMD  git pull && python db_util.py && uwsgi --http-socket :9090 --module gmission --callable app

