# -*- coding: utf-8 -*-

import os
from json import dumps
from raven.contrib.tornado import SentryMixin
from tornado.web import RequestHandler, HTTPError
from tornado.httpclient import AsyncHTTPClient
import delegator
import tempfile


class GitReceivePack(SentryMixin, RequestHandler):
    def prepare(self):
        self.set_header('Expires', 'Fri, 01 Jan 1980 00:00:00 GMT')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Cache-Control', 'no-cache, max-age=0, must-revalidate')
        self.set_header('Content-Type', 'application/x-git-receive-pack-result')

    async def post(self, project_name):
        tmp_dir = self.application.settings['tmp_dir']
        git_dir = os.path.join(tmp_dir, project_name)

        # write the request body to temp file
        fd, temp_path = tempfile.mkstemp(prefix=tmp_dir)
        with open(temp_path, 'wb+') as f:
            f.write(self.request.body)
        os.close(fd)

        # run the git-receive-pack against the new file
        grp_res = delegator.run(''.join((
            'cat %s' % temp_path,
            ' | git-receive-pack --stateless-rpc %s' % git_dir
        )))
        # remove last 4 from output
        # The string `00000000` would end the transmissionx
        # Write new data  ^  in between the 4 zeros.
        self.write(grp_res.out[:-4])

        g_res = delegator.run(''.join((
            'rm %s' % temp_path,
            ' && cd %s' % git_dir,
            ' && git checkout master -q',
            ' && git log -1 --format="%H"',
        )))

        try:
            await AsyncHTTPClient().fetch(
                self.application.settings['engine'],
                method='POST',
                body=dumps({
                    'data': {
                        'repo': project_name,
                        'commit': g_res.out.strip(),
                        'branch': 'master',
                        'user': None
                    }
                }),
                headers={'Content-Type': 'application/json'},
                streaming_callback=self._callback,
                request_timeout=60
            )
        except HTTPError as err:
            self._callback('Error: %s' % err.message)
            self.set_status(500)

        # write the end zeros
        self.write('0000')

        self.finish()

    def _callback(self, chunk):
        """
        Writes via git-receive-pack protocol.
        https://git-scm.com/book/gr/v2/Git-Internals-Transfer-Protocols#_uploading_data
        """
        buffer = 6
        for line in chunk.decode('utf-8').split('\n'):
            lead = ('%x' % (len(line) + buffer)).zfill(4)
            self.write('%s\u0002%s\n' % (lead, line))
