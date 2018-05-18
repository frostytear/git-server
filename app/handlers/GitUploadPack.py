# -*- coding: utf-8 -*-

import delegator
import os.path
from raven.contrib.tornado import SentryMixin
from tornado.web import RequestHandler, HTTPError


class GitUploadPack(SentryMixin, RequestHandler):
    def post(self, project_name):
        dest = os.path.join(self.application.settings['git_dir'], project_name)

        tmp = tempfile.mktemp('')
        with open(tmp, 'wb+') as f:
            f.write(self.request.body)

        res = delegator.run(
            'cat %s | git-upload-pack --stateless-rpc %s' % (tmp, dest)
        )

        self.set_header('Expires', 'Fri, 01 Jan 1980 00:00:00 GMT')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Cache-Control', 'no-cache, max-age=0, must-revalidate')
        self.set_header('Content-Type', 'application/x-git-upload-pack-result')

        self.finish(res.out)
