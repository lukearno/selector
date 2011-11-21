"""Unit test `pliant` and `opliant`."""

import selector


def test_pliant():
    """Transform the WSGI call for a function."""
    outer_environ = {'wsgiorg.routing_args': [
                        ['xxx', 'yyy'],
                        {'z': 'zzz'}]}

    def checker(environ, start_response, x, y, z=None):
        assert environ is outer_environ
        assert start_response == 1
        assert x == 'xxx'
        assert y == 'yyy'
        assert z == 'zzz'
        return 'output'

    product = selector.pliant(checker)
    returned = product(outer_environ, 1)
    assert returned == 'output'


def test_opliant():
    """Transform the WSGI call for an instance method."""
    outer_environ = {'wsgiorg.routing_args': [
                        ['xxx', 'yyy'],
                        {'z': 'zzz'}]}

    def checker(self, environ, start_response, x, y, z=None):
        assert self == 99
        assert environ is outer_environ
        assert start_response == 1
        assert x == 'xxx'
        assert y == 'yyy'
        assert z == 'zzz'
        return 'output'

    product = selector.opliant(checker)
    returned = product(99, outer_environ, 1)
    assert returned == 'output'
