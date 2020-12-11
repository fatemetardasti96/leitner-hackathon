FROM python:3.7-buster

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./scripts/* /usr/local/bin/
COPY . /app
COPY . /assets
WORKDIR /app

# The http port
EXPOSE 4242

CMD run
