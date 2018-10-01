import json
import logging
import os
import re
import subprocess
import tempfile
import urllib

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options


logger = logging.getLogger('texoid')

define("port", default=8888, help="run on the given port", type=int)
define("address", default="localhost", help="run on the given address", type=str)

redimensions = re.compile('.*?(\d+)x(\d+).*?')

LATEX_PATH = os.environ.get('LATEX_BIN', '/usr/bin/latex')
DVISVGM_PATH = os.environ.get('DVISVGM_BIN', '/usr/bin/dvisvgm')
CONVERT_PATH = os.environ.get('CONVERT_BIN', '/usr/bin/convert')

for path in [LATEX_PATH, DVISVGM_PATH, CONVERT_PATH]:
    if os.path.exists(path) and os.path.isfile(path):
        continue
    raise AssertionError('necessary file "%s" does not exist or is not a file' % path)


def svg_to_png(svg):
    # Must use /dev/stdin since some versions of ImageMagick hang with - as input
    comp = subprocess.Popen([CONVERT_PATH, '-identify', 'svg:/dev/stdin', 'png:-'], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = comp.communicate(svg)
    if comp.returncode:
        logger.error(err)
        raise AssertionError('convert exited with error code')
    first_nl = out.find('\n')
    ident = out[:first_nl]

    dim = redimensions.match(ident)
    width = dim.group(1)
    height = dim.group(2)

    out = out[first_nl + 1:]
    return out, width, height


def dvi_to_svg(filename):
    comp = subprocess.Popen([DVISVGM_PATH, '--verbosity=1', '--no-fonts', '--stdout', filename], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    out = comp.communicate()[0]
    if comp.returncode:
        logger.error(out)
        raise AssertionError('dvisvgm exited with error code')
    if 'ERROR' in out:
        raise AssertionError(out)
    return out


def latex_to_dvi(filename):
    comp = subprocess.Popen(
        [LATEX_PATH, '-halt-on-error', '-interaction=nonstopmode', '-output-directory=%s' % os.path.dirname(filename),
         filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = comp.communicate()[0]
    if comp.returncode:
        logger.error(out)
        raise AssertionError(out)
    return filename.replace('.latex', '.dvi')


class MainHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        super(MainHandler, self).set_default_headers()
        self.set_header('Content-Type', 'application/json')

    def handle_request(self):
        try:
            data = urllib.unquote(self.get_argument('q'))
            with tempfile.NamedTemporaryFile(suffix='.latex') as raw:
                raw.write(data)
                raw.flush()

                filename = latex_to_dvi(raw.name)
                svg_data = dvi_to_svg(filename).strip()
                png_data, width, height = svg_to_png(svg_data)
                png_data = png_data.strip().encode('base64')
                return {
                    'success': True,
                    'svg': svg_data,
                    'png': png_data,
                    'meta': {'width': width,
                             'height': height}
                }
        except Exception as error:
            logger.exception('failed to render input')
            return {
                'success': False,
                'error': error.message
            }

    def post(self):
        self.write(json.dumps(self.handle_request()))


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port, address=options.address)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
