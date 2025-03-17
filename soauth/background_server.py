import logging
from multiprocessing.context import Process
import socket
import time

from werkzeug import Request, Response
from werkzeug.serving import make_server


logger = logging.getLogger(__name__)


def allocate_free_port() -> int:
    """
    Allocates a free port on localhost
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def werkzeug_application(environ, start_response):
    request = Request(environ)
    response = Response(
        f"Hello from Werkzeug! You're at {request.path}", mimetype="text/plain"
    )
    return response(environ, start_response)


def run_werkzeug_subprocess(port: int):
    """
    Runs a werkzeug server in a subprocess
    """
    server = make_server("localhost", port, werkzeug_application)
    logger.debug("Starting development server at http://localhost:%d", port)
    server.serve_forever()


def run_werkzeug_server():
    """
    Runs a werkzeug server in the background.

    @TODO: Convert to a context manager
    @TODO: A flow instance will need to be passed in here. This will define the URL, credentials, etc.
    """
    port = allocate_free_port()
    logger.debug("Found a free port %d", port)

    werkzeug_process = Process(target=run_werkzeug_subprocess, args=(port,))
    werkzeug_process.start()
    time.sleep(5)
    werkzeug_process.terminate()
    logger.debug("Development server terminated")
