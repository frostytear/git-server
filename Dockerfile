FROM          node:9.7-alpine
COPY          . .
RUN           npm install
ENV           DIR /asyncy/git
ENV           GRAPHQL_URL http://graphql-private
ENTRYPOINT    ["node", "lib/server.js"]
