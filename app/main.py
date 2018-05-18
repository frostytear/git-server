# -*- coding: utf-8 -*-

import os
from tornado import ioloop
from tornado.options import define, options
from tornado.web import Application
from raven.contrib.tornado import AsyncSentryClient

from . import handlers


define('debug', default=False, help='enable debug')
define('port',
       default=int(os.getenv('PORT', '8888')),
       help='port to listen on')
define('sentry_dsn',
       default=os.getenv('SENTRY_DSN'),
       help='Sentry DSN')
define('engine_addr',
       default=os.getenv('ENGINE_ADDR', 'engine:8888'),
       help='engine hostname:port')
define('git_dir',
       default=os.getenv('GIT_DIR', os.path.join(os.getcwd(), './tmp')),
       help='Location to start git assets')


def make_app():

    _handlers = [
        (r'/(?P<project_name>.+)/info/refs', handlers.InfoRefs),
        (r'/(?P<project_name>.+)/git-receive-pack', handlers.GitReceivePack)
    ]

    app = Application(
        handlers=_handlers,
        debug=options.debug,
        engine_addr=options.engine_addr,
        git_dir=options.git_dir
    )

    app.sentry_client = AsyncSentryClient(options.sentry_dsn)

    return app


if __name__ == '__main__':
    options.parse_command_line()
    app = make_app()
    app.listen(options.port)
    ioloop.IOLoop.current().start()
