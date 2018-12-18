import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line

from texoid.backends import DirectLaTeXBackend, DockerLaTeXBackend
from texoid.server import MainHandler


def main():
    define('port', default=8888, help='run on the given port', type=int)
    define('address', default='localhost', help='run on the given address', type=str)
    define('docker', default=False, help='run with docker', type=bool)
    parse_command_line()

    backend = [DirectLaTeXBackend, DockerLaTeXBackend][options.docker]()
    application = tornado.web.Application([
        (r'/', MainHandler.with_backend(backend)),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port, address=options.address)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
