FROM python:3.7.0-slim-stretch AS base
RUN apt-get update && \
    apt-get install -y vim git build-essential
RUN pip install --upgrade pip

FROM base
COPY requirements /opt/requirements
RUN pip install -r /opt/requirements/dev.txt

COPY /token_platform /usr/src/token_platform
WORKDIR /usr/src
EXPOSE 80
CMD ["python -u /usr/src/token_platform/server.py"]
