# -*- coding: utf-8 -*-

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
        dest = os.path.join(self.application.settings['git_dir'], project_name)

        tmp = tempfile.mktemp('')
        with open(tmp, 'wb+') as f:
            f.write(self.request.body)

        res = delegator.run(''.join((
            'cat %s' % tmp,
            ' | git-receive-pack --stateless-rpc %s' % dest,
            ' && cd %s' % dest,
            ' && git checkout master',
            ' && rm -rf .git'
        )))

        self.set_header('Expires', 'Fri, 01 Jan 1980 00:00:00 GMT')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Cache-Control', 'no-cache, max-age=0, must-revalidate')
        self.set_header('Content-Type', 'application/x-git-receive-pack-result')

        self.write(res.out)

        # [TODO] build project

        self.finish()
