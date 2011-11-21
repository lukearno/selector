"""A few simple WSGI apps for testing."""


def here_i_am(environ, start_response):
    """Just says "Here I am."."""
    start_response("200 OK", [('Content-type', 'text/plain')])
    return ["Here I am."]


def say_hello(environ, start_response):
    """Say hello to named arg "name"."""
    args, kwargs = environ['wsgiorg.routing_args']
    start_response("200 OK", [('Content-type', 'text/plain')])
    return ["Hello %s!" % kwargs['name']]


def say_hello_positional(environ, start_response):
    """Say hello to first positional arg."""
    args, kwargs = environ['wsgiorg.routing_args']
    start_response("200 OK", [('Content-type', 'text/plain')])
    return ["Hello %s!" % args[0]]
