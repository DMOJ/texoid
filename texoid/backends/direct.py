import logging
import os
import re
import shutil
import subprocess
import tempfile

from tornado import gen
from tornado.process import Subprocess

from texoid.utils import utf8bytes, utf8text

logger = logging.getLogger('texoid')
redimensions = re.compile(br'.*?(\d+)x(\d+).*?')


class DirectLaTeXBackend(object):
    def __init__(self):
        self.latex_path = os.environ.get('LATEX_BIN', '/usr/bin/latex')
        self.dvisvgm_path = os.environ.get('DVISVGM_BIN', '/usr/bin/dvisvgm')
        self.convert_path = os.environ.get('CONVERT_BIN', '/usr/bin/convert')

        for path in [self.latex_path, self.dvisvgm_path, self.convert_path]:
            if not os.path.isfile(path):
                raise RuntimeError('necessary file "%s" is not a file' % path)

    @gen.coroutine
    def render(self, source):
        with DirectLaTeXWorker(self) as worker:
            result = yield worker.render(source)
        return result


class DirectLaTeXWorker(object):
    devnull = open(os.devnull)

    def __init__(self, backend):
        self.backend = backend

    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.dir)

    @gen.coroutine
    def render(self, source):
        with open(os.path.join(self.dir, 'render.tex'), 'wb') as f:
            f.write(utf8bytes(source))

        yield self.latex_to_dvi()
        yield self.dvi_to_svg()
        png, width, height = yield self.svg_to_png()
        with open(os.path.join(self.dir, 'render.svg'), 'rb') as f:
            svg = utf8text(f.read())
        return {'png': png, 'svg': svg, 'meta': {'width': width, 'height': height}}

    @gen.coroutine
    def svg_to_png(self):
        convert = Subprocess(
            [self.backend.convert_path, '-identify', 'render.svg', 'png:-'], cwd=self.dir,
            stderr=Subprocess.STREAM, stdin=self.devnull, stdout=Subprocess.STREAM
        )
        out, err = yield [convert.stdout.read_until_close(), convert.stderr.read_until_close()]
        try:
            yield convert.wait_for_exit()
        except subprocess.CalledProcessError:
            raise RuntimeError('Failed to run convert, full log:\n' + utf8text(err, errors='backslashreplace'))

        ident, _, out = out.partition(b'\n')
        width, height = redimensions.match(ident).groups()
        return out, int(width), int(height)

    @gen.coroutine
    def dvi_to_svg(self):
        dvisvgm = Subprocess(
            [self.backend.dvisvgm_path, '--verbosity=1', '--no-fonts', 'render.dvi'],
            stdout=Subprocess.STREAM, stderr=subprocess.STDOUT, cwd=self.dir
        )

        log = yield dvisvgm.stdout.read_until_close()
        try:
            yield dvisvgm.wait_for_exit()
        except subprocess.CalledProcessError:
            raise RuntimeError('Failed to run dvisvgm, full log:\n' + utf8text(log, errors='backslashreplace'))

    @gen.coroutine
    def latex_to_dvi(self):
        latex = Subprocess([
            self.backend.latex_path, '-halt-on-error', '-interaction=nonstopmode', 'render.tex'
        ], stdout=Subprocess.STREAM, stderr=subprocess.STDOUT, cwd=self.dir)

        log = yield latex.stdout.read_until_close()
        try:
            yield latex.wait_for_exit()
        except subprocess.CalledProcessError:
            raise RuntimeError('Failed to run latex, full log:\n' + utf8text(log, errors='backslashreplace'))
