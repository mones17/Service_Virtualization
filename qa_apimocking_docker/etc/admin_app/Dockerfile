FROM python:3.11
WORKDIR /home/python/app
RUN pip install --no-cache-dir newrelic
COPY /requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /home/python/app
CMD newrelic-admin run-program python -c "import newrelic.agent; newrelic.agent.initialize('/home/python/app/newrelic.ini'); import uvicorn; from main import app; uvicorn.run(app, host='admin_app', port=8002)"