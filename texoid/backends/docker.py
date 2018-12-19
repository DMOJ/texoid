import struct
import subprocess

from tornado import gen
from tornado.process import Subprocess

from texoid.utils import utf8bytes, utf8text

header = struct.Struct('!III')
size_struct = struct.Struct('!I')


class DockerLaTeXBackend(object):
    def __init__(self):
        subprocess.call(['docker', 'pull', 'dmoj/texbox:latest'])

    @gen.coroutine
    def _write_and_close(self, stream, input):
        yield stream.write(input)
        stream.close()

    @gen.coroutine
    def render(self, source):
        proc = Subprocess(['docker', 'run', '-i', 'dmoj/texbox:latest'], stdin=Subprocess.STREAM,
                          stdout=Subprocess.STREAM, stderr=Subprocess.STREAM)
        input = self._write_and_close(proc.stdin, utf8bytes(source))
        _, output, log = yield [input, proc.stdout.read_until_close(), proc.stderr.read_until_close()]

        try:
            yield proc.wait_for_exit()
        except subprocess.CalledProcessError:
            raise RuntimeError('Failed to run docker, full log:\n' + utf8text(log, errors='backslashreplace'))

        try:
            width, height, svg_len = header.unpack(output[:header.size])
            svg = output[header.size:header.size + svg_len]
            rest = output[header.size + svg_len:]
            png_len, = size_struct.unpack(rest[:size_struct.size])
            png = rest[size_struct.size:size_struct.size + png_len]
        except struct.error:
            raise RuntimeError('corrupted output from texbox')

        if len(svg) != svg_len or b'<svg' not in svg:
            raise RuntimeError('corrupted SVG file from texbox')

        if len(png) != png_len or b'\x89PNG' not in png:
            raise RuntimeError('corrupted PNG file from texbox')

        return {'svg': utf8text(svg), 'png': png, 'meta': {'width': width, 'height': height}}
