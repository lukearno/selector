"""Unit test Selector.select()."""

import selector

from . import mocks


def test_select_first_match():
    """Select the first matching regex."""
    s = selector.Selector()
    s.mappings = [
        (mocks.mock_regex(), {'GET': 1}),
        (mocks.mock_regex('/foo'), {'GET': 2}),
        (mocks.mock_regex(), {'GET': 3}),
        (mocks.mock_regex('/foo', {'name': 'bar'}), {'GET': 4}),
    ]
    app, svars, methods, matched = s.select('/foo', 'GET')
    assert app == 2
    assert svars == {}
    assert methods == ['GET']
    assert matched == "/foo"


def test_select_match_any_http_method():
    """Select the first matching regex."""
    s = selector.Selector()
    s.mappings = [
        (mocks.mock_regex(), {'GET': 1}),
        (mocks.mock_regex('/foo'), {'_ANY_': 2}),
        (mocks.mock_regex(), {'GET': 3}),
        (mocks.mock_regex('/foo', {'name': 'bar'}), {'GET': 4}),
    ]
    app, svars, methods, matched = s.select('/foo', 'GET')
    assert app == 2
    assert svars == {}
    assert methods == ['_ANY_']
    assert matched == "/foo"


def test_select_405():
    """The path matches but the method is not supported."""
    s = selector.Selector()
    s.mappings = [
        (mocks.mock_regex(), {'GET': 1}),
        (mocks.mock_regex('/foo'), {'POST': 2}),
    ]
    app, svars, methods, matched = s.select('/foo', 'GET')
    assert app is s.status405
    assert svars == {}
    assert methods == ['POST']
    assert matched == ""


def test_select_404():
    """The path was not matched."""
    s = selector.Selector()
    s.mappings = [
        (mocks.mock_regex(), {'GET': 1}),
    ]
    app, svars, methods, matched = s.select('/foo', 'GET')
    assert app is s.status404
    assert svars == {}
    assert methods == []
    assert matched == ""
