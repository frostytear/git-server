# -*- coding: utf-8 -*-

import subprocess
import os.path
from raven.contrib.tornado import SentryMixin
from tornado.web import RequestHandler, HTTPError
import delegator
import shutil


class InfoRefs(SentryMixin, RequestHandler):
    def get(self, project_name):
        service = self.get_argument('service')
        if service != 'git-receive-pack':
            raise HTTPError(405)

        dest = os.path.join(self.application.settings['git_dir'], project_name)

        if os.path.exists(dest):
            shutil.rmtree(dest)
        os.makedirs(dest)
        delegator.run(' '.join((
            'cd', dest, '&&',
            'git', 'init', '&&',
            'git', 'config', '--add', 'receive.denyCurrentBranch', 'ignore'
        )))

        self.set_header('Expires', 'Fri, 01 Jan 1980 00:00:00 GMT')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Cache-Control', 'no-cache, max-age=0, must-revalidate')
        self.set_header('Content-Type',
                        'application/x-%s-advertisement' % service)

        packet = '# service=%s\n' % service
        print(service)
        length = len(packet) + 4
        prefix = '{:04x}'.format(length & 0xFFFF)
        self.write(''.join((prefix, packet, '0000')))

        # [TODO] this data will always be the same
        res = delegator.run(
            '%s --stateless-rpc --advertise-refs %s' % (service, dest)
        )
        self.write(res.out)

        self.finish()
