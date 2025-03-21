from enum import StrEnum
import logging
from multiprocessing.context import Process
from multiprocessing import Queue
import socket
from typing import Callable
import webbrowser

from werkzeug import Request, Response
from werkzeug.serving import make_server


logger = logging.getLogger(__name__)


class QueueMessage(StrEnum):
    SHUTDOWN = "shutdown"


class BackgroundServer:
    port: int
    queue: Queue
    werkzeug_process: Process

    def __init__(self):
        self.port = self.allocate_free_port()
        self.queue = Queue()
        self.start()
        self.read_queue()

    def allocate_free_port(self) -> int:
        """
        Allocates a free port on localhost
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            port = s.getsockname()[1]
            logger.info("Allocating free port: %d", port)
            return port

    def werkzeug_subprocess_worker(self):
        """
        Runs a werkzeug server in a subprocess
        """
        shutdown_count = 3

        # @TODO: This should become a class
        def werkzeug_application(environ: dict, start_response: Callable):
            nonlocal shutdown_count

            request = Request(environ)
            response = Response(
                f"Hello from Werkzeug! Requests until shutdown: {shutdown_count}",
                mimetype="text/plain",
            )
            shutdown_count -= 1
            if not shutdown_count:
                self.queue.put(QueueMessage.SHUTDOWN)

            return response(environ, start_response)

        server = make_server("localhost", self.port, werkzeug_application)
        logger.debug(
            "Running Werkzeug development server at http://localhost:%d", self.port
        )
        server.serve_forever()

    def read_queue(self):
        """
        Reads the pipe-based queue for messages.
        If 'shutdown' is received,
        """
        while True:
            message = self.queue.get()
            logging.debug("Received from queue: %s", message)
            if message is QueueMessage.SHUTDOWN:
                return self.terminate()

    def start(self):
        self.werkzeug_process = Process(target=self.werkzeug_subprocess_worker)
        self.werkzeug_process.start()
        webbrowser.open(f"http://localhost:{self.port}")

    def terminate(self):
        logger.debug("Terminating Werkzeug development server")
        self.werkzeug_process.terminate()
