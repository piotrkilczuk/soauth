import logging

from soauth.background_server import run_werkzeug_server


def main():
    logging.basicConfig(level=logging.DEBUG)
    run_werkzeug_server()