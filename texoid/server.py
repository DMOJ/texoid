import json
import logging
from base64 import b64encode
from urllib.parse import unquote

import tornado.web
from tornado import gen

logger = logging.getLogger('texoid')


class MainHandler(tornado.web.RequestHandler):
    @classmethod
    def with_backend(cls, backend):
        return type('MainHandler', (cls,), {'backend': backend})

    @gen.coroutine
    def post(self):
        self.set_header('Content-Type', 'application/json')
        try:
            if self.request.headers.get('Content-Type', 'text/plain') == 'application/x-www-form-urlencoded':
                data = unquote(self.get_argument('q'))
            else:
                data = self.request.body
            result = yield self.backend.render(data)
            result['success'] = True
            result['png'] = b64encode(result['png']).decode('ascii')
            self.write(json.dumps(result))
        except Exception as error:
            logger.exception('failed to render input')
            self.write(json.dumps({
                'success': False,
                'error': error.args[0]
            }))
