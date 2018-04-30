FROM          node:9.7-alpine
COPY          . .
RUN           npm install
ENV           DIR /tmp/git
ENTRYPOINT    ["node", "lib/server.js"]
