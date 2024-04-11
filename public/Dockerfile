FROM node:20.11.0-alpine AS node
FROM python:3.12.2-alpine3.19

COPY --from=node /usr/lib /usr/lib
COPY --from=node /usr/local/lib /usr/local/lib
COPY --from=node /usr/local/include /usr/local/include
COPY --from=node /usr/local/bin /usr/local/bin

WORKDIR /app

EXPOSE 5000
ENV FLASK_APP=worker-public.py

COPY . /app
RUN pip install -r requirements.txt
RUN npm install

ENTRYPOINT [ "flask"]
CMD [ "run", "--host", "0.0.0.0" ]
