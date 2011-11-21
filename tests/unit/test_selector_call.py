"""Unit test `Selector.__call__()`."""

from flexmock import flexmock

import selector


def test_selector_call():
    """Call should call select, munge environ and call app."""
    s = selector.Selector()

    def checker(environ, start_response):
        print environ
        assert len(environ.keys()) == 7
        assert start_response == 1
        assert environ['selector.methods'] == ['GET', 'POST']
        assert environ['selector.vars'] == {'1': 'two',
                                            '0': 'one',
                                            'name': 'luke'}
        assert environ['wsgiorg.routing_args'][0] == ['one', 'two']
        assert environ['wsgiorg.routing_args'][1] == {'name': 'luke'}
        assert environ['PATH_INFO'] == ''
        assert environ['SCRIPT_NAME'] == '/path'
        assert environ['REQUEST_METHOD'] == 'GET'
        return 'output'

    # Mock select
    (flexmock(s)
     .should_receive('select')
     .once
     .with_args('/path', 'GET')
     .replace_with(lambda x, y: (
        checker,
        {'name': 'luke',
         '__pos0': 'one',
         '__pos1': 'two'},
        ['GET', 'POST'],
        '/path')))
    returned = s({'PATH_INFO': '/path', 'REQUEST_METHOD': 'GET'}, 1)
    assert returned == 'output'
