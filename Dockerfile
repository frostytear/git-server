FROM          jfloff/alpine-python:recent
COPY          . .
RUN           apk add git && pip install -r requirements.txt
ENV           DIR /asyncy
ENV           GRAPHQL_URL http://graphql-private
ENTRYPOINT    ["python", "-m", "app.main"]
