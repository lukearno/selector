"""Unit test `Selector` mapping file handling."""

import pytest
import resolver

from flexmock import flexmock

import selector

from . import mocks


def test__line_parse_comments_and_blanks_ignored():
    """Blank and are ignored by the parser."""
    s = flexmock(selector.Selector())
    assert s._parse_line("", None, None) == (None, None)
    assert s._parse_line("  # ", None, None) == (None, None)
    assert s._parse_line("", 1, 2) == (1, 2)
    assert s._parse_line("  # ", 3, 4) == (3, 4)


def test__line_parse_processing_directives():
    """Route adding is modulated by `@` directives."""
    flexmock(resolver).should_receive('resolve').replace_with(lambda x: 1)
    s = flexmock(selector.Selector(), add=None)
    assert s.prefix == ''
    assert s._parse_line("@prefix /pre", None, None) == (None, None)
    assert s.prefix == '/pre'
    assert s._parse_line("@prefix", None, None) == (None, None)
    assert s.prefix == ''
    assert s.parser.__class__ is selector.SimpleParser
    assert s._parse_line("@parser whatever", None, None) == (None, None)
    assert s.parser == 1
    assert s.wrap == None
    assert s._parse_line("@wrap whatever", None, None) == (None, None)
    assert s.wrap == 1


def test__line_parse_path_expressions_and_http_methods():
    """Path expressions collect HTTP method -> handler maps."""
    flexmock(resolver).should_receive('resolve').replace_with(lambda x: 1)
    s = flexmock(selector.Selector(), add=None)
    s.should_receive('add').once
    assert s._parse_line("/path", None, None) == ('/path', {})
    assert (s._parse_line("  GET foo:Bar", '/path', {})
            == ('/path', {'GET': 1}))
    assert (s._parse_line("  PUT foo:Put", '/path', {'GET': 1})
            == ('/path', {'PUT': 1, 'GET': 1}))
    assert (s._parse_line("/bar", '/path', {'GET': 1})
            == ('/bar', {}))
    print dir(s)


def test_selector_slurp_file():
    """Slurping a file adds mappings.."""
    flexmock(resolver).should_receive('resolve').replace_with(lambda x: 1)
    mocks.mock_open('test_selector_slurp_file', [
        "/some-url/",
        "    GET whatever.foo:app"])
    s = selector.Selector()
    (flexmock(s)
     .should_receive('add')
     .once.with_args('/some-url/', {'GET': 1})
     .replace_with(mocks.checkadd(s, '', s.parser, None)))
    s.slurp_file('test_selector_slurp_file')


def test_selector_slurp_file_with_options():
    """Slurp in a file with the works.."""
    flexmock(resolver).should_receive('resolve').replace_with(lambda x: 1)
    mocks.mock_open('test_selector_slurp_file', [
        "/some-url/",
        "    GET whatever.foo:app"])
    s = selector.Selector()
    (flexmock(s)
     .should_receive('add')
     .once.with_args('/some-url/', {'GET': 1})
     .replace_with(mocks.checkadd(s, '/pre', 2, 3)))
    assert s.prefix == ''
    assert s.parser.__class__ == selector.SimpleParser
    assert s.wrap is None
    s.slurp_file('test_selector_slurp_file',
                 prefix='/pre', parser=2, wrap=3)
    assert s.prefix == ''
    assert s.parser.__class__ == selector.SimpleParser
    assert s.wrap is None


def test_selector_slurp_file_exception():
    """Slurping a file adds mappings.."""
    flexmock(resolver).should_receive('resolve').replace_with(lambda x: 1)
    mocks.mock_open('test_selector_slurp_file', [
        "    GET whatever.foo:app",
        "/some-url/"])
    s = selector.Selector()
    flexmock(s).should_receive('add').times(0)
    with pytest.raises(selector.MappingFileError):
        s.slurp_file('test_selector_slurp_file')
