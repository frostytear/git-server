# -*- coding: utf-8 -*-

import asyncio
import os
import sys
from tornado.options import define, options
from tornado.web import Application
import tornado.platform.asyncio
from raven.contrib.tornado import AsyncSentryClient

from . import handlers


define('debug', default=False, help='enable debug')
define('port',
       default=int(os.getenv('PORT', '8888')),
       help='port to listen on')
define('sentry_dsn',
       default=os.getenv('SENTRY_DSN'),
       help='Sentry DSN')
define('engine',
       default=os.getenv('ENGINE', 'engine:8888'),
       help='engine hostname:port')
define('tmp_dir',
       default=os.getenv('TMP_DIR', os.path.join(os.getcwd(), './tmp/')),
       help='Location to start git assets')


def make_app():

    _handlers = [
        (r'/(?P<project_name>.+)/info/refs', handlers.InfoRefs),
        (r'/(?P<project_name>.+)/git-receive-pack', handlers.GitReceivePack)
    ]

    app = Application(
        handlers=_handlers,
        debug=options.debug,
        engine=options.engine,
        tmp_dir=options.tmp_dir
    )

    app.sentry_client = AsyncSentryClient(options.sentry_dsn)

    return app


if __name__ == '__main__':
    try:
        options.parse_command_line()
        tornado.platform.asyncio.AsyncIOMainLoop().install()
        app = make_app()
        app.listen(options.port)
        asyncio.get_event_loop().run_forever()

    except KeyboardInterrupt:
        sys.stdout.write('Goodbye.')
