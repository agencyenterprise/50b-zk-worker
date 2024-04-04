FROM python:3.12.2-alpine3.19

WORKDIR /app

EXPOSE 5000
ENV FLASK_APP=worker-public.py

COPY . /app
RUN pip install -r requirements.txt

ENTRYPOINT [ "flask"]
CMD [ "run", "--host", "0.0.0.0" ]
