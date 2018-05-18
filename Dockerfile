FROM          python
COPY          . .
RUN           pip install -r requirements.txt
ENV           GIT_DIR /asyncy/git
ENV           GRAPHQL_URL http://graphql-private
ENTRYPOINT    ["python", "-m", "app.main"]
