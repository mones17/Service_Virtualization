FROM cassandra:4.1
USER root
RUN apt-get update && apt-get install -y python3.9 python3-pip
RUN mkdir -p /var/lib/cassandra && chown -R cassandra:cassandra /var/lib/cassandra
EXPOSE 8010
RUN mkdir -p /var/lib/backups
RUN chmod 777 /var/lib/backups
WORKDIR /home/python/app
COPY /requirements.txt /code/requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /home/python/app
RUN chmod +x ./start.sh
RUN chmod +x ./create-backup.sh
USER cassandra
RUN mkdir -p /var/lib/cassandra && chown -R cassandra:cassandra /var/lib/cassandra
CMD ["sh", "start.sh"]