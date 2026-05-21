"""Catch-all handler that returns 404.html with a proper 404 status code.

All known routes are served as static files by App Engine (see app.yaml).
Any request that falls through to this handler is, by definition, a 404.
"""

import pathlib

_404_HTML = pathlib.Path(__file__).with_name("404.html").read_text()


def app(environ, start_response):
    start_response("404 Not Found", [("Content-Type", "text/html; charset=utf-8")])
    return [_404_HTML.encode()]
