from __future__ import annotations

from enum import StrEnum
import logging
from multiprocessing.context import Process
from multiprocessing import Queue
import socket
from typing import Callable, Iterable
import webbrowser

from jinja2 import Environment, FileSystemLoader
from werkzeug import Request, Response
from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, Rule
from werkzeug.serving import make_server

from soauth.const import PATHS

logger = logging.getLogger(__name__)


class QueueMessage(StrEnum):
    SHUTDOWN = "shutdown"


class ApplicationFlow:
    queue: Queue
    url_map: Map
    jinja_env: Environment

    def __init__(self, queue: Queue):
        self.queue = queue
        self.setup_urls()
        self.setup_jinja2()

    def index(self, request: Request) -> dict:
        return {}

    def setup_urls(self):
        self.url_map = Map([Rule("/", endpoint=self.index)])

    def setup_jinja2(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(PATHS.TEMPLATES), autoescape=True
        )

    def render_template(self, template_name: str, context: dict) -> str:
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)

    def dispatch_request(self, request: Request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            context = endpoint(request, **values)
            template = self.jinja_env.get_template(f"{endpoint.__name__}.html")
            return Response(template.render(context), mimetype="text/html")
        except HTTPException as e:
            return e

    # def dispatch_request(self, request: Request) -> Response:
    #     self.queue.put(QueueMessage.SHUTDOWN)
    #     return Response("Hello world")

    def wsgi_app(self, environ: dict, start_response: Callable) -> Iterable[bytes]:
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ: dict, start_response: Callable) -> Iterable[bytes]:
        return self.wsgi_app(environ, start_response)


class BackgroundServer:
    app: ApplicationFlow
    port: int
    queue: Queue
    werkzeug_process: Process

    def __init__(self):
        self.port = self.allocate_free_port()
        self.queue = Queue()
        self.app = self.setup_werkzeug_app(self.queue)
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

    def setup_werkzeug_app(self, queue: Queue) -> ApplicationFlow:
        """
        Sets up the Werkzeug application. This should inherit from ApplicationFlow.
        """
        app = ApplicationFlow(queue)
        return app

    def werkzeug_subprocess_worker(self):
        """
        Runs a werkzeug server in a subprocess
        """
        server = make_server("localhost", self.port, self.app)
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
