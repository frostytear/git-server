FROM          jfloff/alpine-python:recent
COPY          . .
RUN           apk add git && pip install -r requirements.txt
ENV           TMP_DIR /asyncy/git
ENV           GRAPHQL_URL http://graphql-private
ENTRYPOINT    ["python", "-m", "app.main"]
