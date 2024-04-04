FROM python:3.12.2-alpine3.19

WORKDIR /app

COPY . /app
RUN pip install -r requirements.txt

CMD ["/usr/local/bin/python3", "/app/worker-secure.py"]
