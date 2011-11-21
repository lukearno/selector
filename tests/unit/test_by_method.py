"""Unit tests for `ByMethod()`."""

from flexmock import flexmock

import selector


class Methodical(selector.ByMethod):
    """Mock subclass of `ByMethod`."""

    def GET(self, environ, start_response):
        """Do Nothing."""

    def POST(self, environ, start_response):
        """Do Nothing."""


def test_by_method_exists():
    """Route by HTTP method to corresponding method."""
    methodical = Methodical()
    flexmock(methodical).should_receive('GET').once
    environ = {'REQUEST_METHOD': 'GET'}
    methodical(environ, None)
    print environ
    assert 'GET' in environ['selector.methods']
    assert 'POST' in environ['selector.methods']


def test_by_method_doesnt_exist():
    """Route by HTTP method should call it's 405 fallback."""
    methodical = Methodical()
    (flexmock(methodical).should_receive('_method_not_allowed').once
     .replace_with(lambda x, y: None))
    environ = {'REQUEST_METHOD': 'PUT'}
    methodical(environ, None)
    assert 'GET' in environ['selector.methods']
    assert 'POST' in environ['selector.methods']


def test_method_not_allowed_uses_selector():
    """We are using the default 405 handler."""
    assert selector.ByMethod._method_not_allowed is selector.method_not_allowed
