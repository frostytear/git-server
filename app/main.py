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
       type=int,
       default=os.getenv('PORT', '8888'),
       help='port to listen on')
define('sentry_dsn',
       default=os.getenv('SENTRY_DSN'),
       help='Sentry DSN')
define('deploy_url',
       default=os.getenv('DEPLOY_URL', 'http://engine:8888/story/run'),
       help='Location to post payload of deployment')
define('story',
       default=os.getenv('STORY'),
       help='Story to run when releasing')
define('dir',
       default=os.getenv('DIR', os.path.join(os.getcwd(), './tmp/')),
       help='Location to start git assets')


def make_app():

    _handlers = [
        (r'/(?P<project_name>.+)/info/refs', handlers.InfoRefs),
        (r'/(?P<project_name>.+)/git-receive-pack', handlers.GitReceivePack)
    ]

    app = Application(
        handlers=_handlers,
        debug=options.debug
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
