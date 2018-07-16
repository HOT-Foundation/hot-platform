FROM registry-hotnow.proteus-tech.com/base-hotnow-htkn-platform:1.2.0

COPY requirements /opt/requirements
RUN pip install --upgrade pip
RUN pip install -r /opt/requirements/dev.txt

COPY /token_platform /usr/src/token_platform

WORKDIR /usr/src

EXPOSE 80

CMD ["python -u /usr/src/token_platform/server.py"]
