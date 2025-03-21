import logging

from soauth.background_server import BackgroundServer


def main():
    logging.basicConfig(level=logging.DEBUG)
    BackgroundServer()
