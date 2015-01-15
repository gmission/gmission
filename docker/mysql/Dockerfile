FROM tutum/mysql

ENV MYSQL_USER csp_team
ENV MYSQL_PASS csp2014hkust
ENV MYSQL_DATABASE gmission_hkust

ADD ./init.sh /init.sh

RUN chmod 755 /*.sh


CMD /init.sh&&/run.sh
