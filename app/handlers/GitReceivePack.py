# -*- coding: utf-8 -*-

import os
from json import dumps
from raven.contrib.tornado import SentryMixin
from tornado.web import RequestHandler, HTTPError
from tornado.httpclient import AsyncHTTPClient
from tornado.options import options
import delegator
import tempfile


class GitReceivePack(SentryMixin, RequestHandler):

    def prepare(self):
        self.set_header('Expires', 'Fri, 01 Jan 1980 00:00:00 GMT')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Cache-Control', 'no-cache, max-age=0, must-revalidate')
        self.set_header('Content-Type', 'application/x-git-receive-pack-result')

    async def post(self, project_name):
        git_dir = os.path.join(options.dir, project_name)

        # write the request body to temp file
        fd, temp_path = tempfile.mkstemp(prefix=options.dir)
        with open(temp_path, 'wb+') as f:
            f.write(self.request.body)
        os.close(fd)

        # run the git-receive-pack against the new file
        grp_res = delegator.run(
            f'cat {temp_path} | git-receive-pack --stateless-rpc {git_dir}'
        )
        # remove last 4 from output
        # The string `00000000` would end the transmissionx
        # Write new data  ^  in between the 4 zeros.
        self.write(grp_res.out[:-4])

        g_res = delegator.run(
            f'rm {temp_path}'
            f' && cd {git_dir}'
            ' && git checkout master -q'
            ' && git log -1 --format="%H"'
        )

        def streaming_callback(chunk):
            chunk = chunk.decode('utf-8')

            if '**ERROR**' in chunk:
                streaming_callback.error = True
                chunk = chunk.replace('**ERROR**', '')

            self.write(self.pack_chunk(chunk))
            self.flush()

        streaming_callback.error = False

        await AsyncHTTPClient().fetch(
            options.deploy_url,
            method='POST',
            body=dumps({
                'story_name': options.story,
                'function': 'NewRelease',
                'context': {
                    'data': {
                        'repo': project_name,
                        'commit': g_res.out.strip(),
                        'branch': 'master',
                        'user': None
                    }
                }
            }),
            headers={'Content-Type': 'application/json'},
            streaming_callback=streaming_callback,
            request_timeout=60
        )

        # write the end zeros
        self.write('0000')

        if streaming_callback.error:
            streaming_callback((f'ERR failed').encode('utf-8'))
            self.write('0000')

        self.finish()

    def pack_chunk(self, data):
        """
        Writes via git-receive-pack protocol.
        https://git-scm.com/book/gr/v2/Git-Internals-Transfer-Protocols#_uploading_data

        The maximum length of a pkt-line's data component is 65516 bytes.
        Implementations MUST NOT send pkt-line whose length exceeds 65520
        (65516 bytes of payload + 4 bytes of length data).
        """
        buffer = 6
        return ''.join(
            f'{("%x" % (len(line) + buffer)).zfill(4)}\u0002{line}\n'
            for line in data.split('\n')
        )
