# -*- coding: utf-8 -*-

import os
import tornado.ioloop
import tornado.web
from tornado.options import define, options


define('debug', default=False, help='enable debug')
define('port',
       type=int,
       default=os.getenv('PORT', '8889'),
       help='port to listen on')


class MainHandler(tornado.web.RequestHandler):
    def post(self):
        self.write('-----> Fake Engine\n')
        self.write('       Amazing stuff would be happening here...\n')
        self.write('       But there isnt.\n')
        self.write('-----> Request body\n')
        self.write('       %s\n' % self.request.body)
        self.write('\n-----> Visit http://asyncy.com')


def make_app():
    return tornado.web.Application([
        (r'/story/run', MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
