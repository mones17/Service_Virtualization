FROM python:3.11
RUN apt-get update && apt-get install -y libnss3
RUN pip install --no-cache-dir --upgrade newrelic
WORKDIR /home/python/app
COPY /requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /home/python/app
COPY newrelic.ini /home/python/app/newrelic.ini  
CMD newrelic-admin run-program python -c "import newrelic.agent; newrelic.agent.initialize('/home/python/app/newrelic.ini'); import uvicorn; from main import app; uvicorn.run(app, host='python_app', port=8000)"