FROM python:3.9-alpine
RUN apk update && apk add --no-cache nginx
COPY /nginx/sites-available /etc/nginx/sites-available
COPY /nginx/conf/nginx.conf /etc/nginx/nginx.conf
COPY /nginx/ssl/certs/nginx-selfsigned.crt /etc/ssl/certs/nginx-selfsigned.crt
COPY /nginx/ssl/private/nginx-selfsigned.key /etc/ssl/private/nginx-selfsigned.key
COPY /nginx/ssl/certs/dhparam.pem /etc/ssl/certs/dhparam.pem
WORKDIR /home/python/app
COPY ./requirements.txt /code/requirements.txt
COPY . /home/python/app
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
EXPOSE 80
EXPOSE 443
EXPOSE 8001
COPY ./start.sh /home/python/app/start.sh
RUN chmod +x ./start.sh
CMD ["sh", "start.sh"]