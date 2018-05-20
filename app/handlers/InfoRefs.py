# -*- coding: utf-8 -*-

import os.path
from raven.contrib.tornado import SentryMixin
from tornado.web import RequestHandler, HTTPError
from tornado.options import options
import delegator
import shutil


class InfoRefs(SentryMixin, RequestHandler):

    def prepare(self):
        self.set_header('Expires', 'Fri, 01 Jan 1980 00:00:00 GMT')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Cache-Control', 'no-cache, max-age=0, must-revalidate')
        self.set_header('Content-Type',
                        'application/x-git-receive-pack-advertisement')

    def get(self, project_name):
        service = self.get_argument('service')

        # only accept push events
        if service != 'git-receive-pack':
            raise HTTPError(405)

        # get the project destination
        git_dir = os.path.join(options.dir, project_name)
        if os.path.exists(git_dir):
            shutil.rmtree(git_dir)
        os.makedirs(git_dir)

        # intialize the git project
        # denyCurrentBranch is ignored because the project had no branch
        delegator.run(
            f'cd {git_dir}'
            ' && git init'
            ' && git config --add receive.denyCurrentBranch ignore'
        )

        self.finish(
            b'001f# service=git-receive-pack\n'
            b'0000009c0000000000000000000000000000000000000000'
            b' capabilities^{}\x00report-status delete-refs side-band-64k'
            b' quiet atomic ofs-delta agent=git/2.14.3.(Apple.Git-98)\n0000'
        )
