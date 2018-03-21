FROM python:3

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY /aiohttp /usr/src

WORKDIR /usr/src
CMD ["python -u server.py"]