FROM python:3.6.4-slim-jessie

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY /token_platform /usr/src/token_platform

WORKDIR /usr/src
CMD ["python -u /usr/src/token_platform/server.py"]