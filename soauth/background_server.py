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
from werkzeug.exceptions import HTTPException, NotFound, BadRequest
from werkzeug.routing import Map, Rule
from werkzeug.serving import make_server

from soauth.const import PATHS
from soauth.flows import BaseFlow, GoogleAPI

logger = logging.getLogger(__name__)


class QueueMessage(StrEnum):
    SHUTDOWN = "shutdown"


class WSGIApp:
    queue: Queue
    url_map: Map
    jinja_env: Environment
    flows: dict[str, BaseFlow]
    port: int

    def __init__(self, queue: Queue, port: int):
        self.queue = queue
        self.port = port
        self.setup_flows()
        self.setup_urls()
        self.setup_jinja2()

    def index(self, request: Request) -> dict:
        return {}

    def instantiate_flow(self, flow_name: str) -> BaseFlow:
        flow = self.flows.get(flow_name)
        if not flow:
            raise NotFound(f"Flow {flow_name} not found")
        return flow

    def collect_secrets_and_scopes(
        self, request: Request, flow_name: str
    ) -> dict | Response:
        flow = self.instantiate_flow(flow_name)
        form = flow.form(request.form)
        if request.method == "POST" and form.validate():
            consent_screen_args = flow.collect_consent_screen_args(form)
            return flow.redirect_to_consent_screen(consent_screen_args)
        return {"form": form}

    def callback(self, request: Request, flow_name: str) -> dict:
        flow = self.instantiate_flow(flow_name)
        if "code" not in request.args:
            raise BadRequest("No code provided")
        tokens = flow.acquire_tokens(request.args["code"], request.args["state"])
        return {"tokens": tokens}

    def setup_flows(self):
        self.flows = {"google": GoogleAPI(self.port)}

    def setup_urls(self):
        self.url_map = Map(
            [
                Rule("/", endpoint=self.index),
                Rule("/<flow_name>/", endpoint=self.collect_secrets_and_scopes),
                Rule("/<flow_name>/callback/", endpoint=self.callback),
            ]
        )

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
            context_or_response = endpoint(request, **values)
            if isinstance(context_or_response, Response):
                return context_or_response
            template = self.jinja_env.get_template(f"{endpoint.__name__}.html")
            return Response(template.render(context_or_response), mimetype="text/html")
        except HTTPException as e:
            return e

    def wsgi_app(self, environ: dict, start_response: Callable) -> Iterable[bytes]:
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ: dict, start_response: Callable) -> Iterable[bytes]:
        return self.wsgi_app(environ, start_response)


class BackgroundServer:
    app: WSGIApp
    port: int
    queue: Queue
    werkzeug_process: Process

    def __init__(self):
        self.port = self.allocate_free_port()
        self.queue = Queue()
        self.app = self.setup_werkzeug_app(self.queue, self.port)
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

    def setup_werkzeug_app(self, queue: Queue, port: int) -> WSGIApp:
        """
        Sets up the Werkzeug application. This should inherit from ApplicationFlow.
        """
        app = WSGIApp(queue, port)
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
