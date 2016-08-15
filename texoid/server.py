import os
import tempfile
import urllib

import subprocess

import sys
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

LATEX_PATH = os.environ.get('LATEX_BIN', '/usr/bin/latex')
DVISVGM_PATH = os.environ.get('DVISVGM_BIN', '/usr/bin/dvisvgm')
CONVERT_PATH = os.environ.get('CONVERT_BIN', '/usr/bin/convert')

for path in [LATEX_PATH, DVISVGM_PATH, CONVERT_PATH]:
    if os.path.exists(path) and os.path.isfile(path):
        continue
    raise AssertionError('necessary file "%s" does not exist or is not a file' % path)


def svg_to_png(svg):
    comp = subprocess.Popen([CONVERT_PATH, 'svg:-', 'png:/dev/stdout'], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = comp.communicate(svg)
    if comp.returncode:
        print >> sys.stderr, err
        raise AssertionError('convert exited with error code')
    return out


def dvi_to_svg(filename):
    comp = subprocess.Popen([DVISVGM_PATH, '--verbosity=1', '--no-fonts', '--stdout', filename], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    out = comp.communicate()[0]
    if comp.returncode:
        print >> sys.stderr, out
        raise AssertionError('dvisvgm exited with error code')
    if 'ERROR' in out:
        raise AssertionError(out)
    return out


def latex_to_dvi(filename):
    comp = subprocess.Popen(
        [LATEX_PATH, '-halt-on-error', '-output-directory=%s' % os.path.dirname(filename), filename],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = comp.communicate()[0]
    if comp.returncode:
        print >> sys.stderr, out
        raise AssertionError(out)
    return filename.replace('.latex', '.dvi')


class MainHandler(tornado.web.RequestHandler):
    def handle_request(self):
        try:
            data = urllib.unquote(self.get_argument('q'))
            with tempfile.NamedTemporaryFile(suffix='.latex') as raw:
                raw.write(data)
                raw.flush()

                filename = latex_to_dvi(raw.name)
                svg_data = dvi_to_svg(filename).strip()
                png_data = svg_to_png(svg_data).strip().encode('base64')
                return {
                    'status': 'ok',
                    'data': {
                        'svg': svg_data,
                        'png': png_data
                    }}
        except Exception as error:
            print error.message
            return {
                'status': 'error',
                'error_message': error.message
            }

    def get(self):
        self.write(json.dumps(self.handle_request()))


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
