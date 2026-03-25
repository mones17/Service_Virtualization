FROM python:3.11
WORKDIR /home/python/app
COPY /requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /home/python/app
CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "chatbot_app", "--port", "8006"]