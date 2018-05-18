# -*- coding: utf-8 -*-

import os
from raven.contrib.tornado import SentryMixin
from tornado.web import RequestHandler, HTTPError
from io import BytesIO
from dulwich.pack import PackStreamReader
import subprocess
import os.path
import delegator
import tempfile


class GitReceivePack(SentryMixin, RequestHandler):
    def post(self, project_name):
        git_dir = self.application.settings['git_dir']
        dest = os.path.join(git_dir, project_name)

        fd, temp_path = tempfile.mkstemp(prefix=git_dir)
        with open(temp_path, 'wb+') as f:
            f.write(self.request.body)
        os.close(fd)

        res = delegator.run(''.join((
            'cat %s' % temp_path,
            ' | git-receive-pack --stateless-rpc %s' % dest,
            ' && rm %s' % temp_path,
            ' && cd %s' % dest,
            ' && git checkout master -q',
            ' && rm -rf .git'
        )))

        self.set_header('Expires', 'Fri, 01 Jan 1980 00:00:00 GMT')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Cache-Control', 'no-cache, max-age=0, must-revalidate')
        self.set_header('Content-Type', 'application/x-git-receive-pack-result')

        self.write(res.out.replace('00000000', '0000'))

        # [TODO] build project and stream output here
        # https://gist.github.com/maxogden/8925627
        self.write('000C\u0002hello!\n')  # WORKS
        self.write('000C\u0002hello!\n')  # WORKS
        self.write('000C\u0002hello!\n')  # WORKS

        # finish the message
        self.write('0000')

        self.finish()
