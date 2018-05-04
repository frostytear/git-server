FROM          node:9.7-alpine
COPY          . .
RUN           npm install
ENV           DIR /asyncy/git
ENTRYPOINT    ["node", "lib/server.js"]
