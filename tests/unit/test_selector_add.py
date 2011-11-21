"""Unit tests for Selector.add().."""

import re

from flexmock import flexmock

import selector


def test_add_keyword():
    """Add mapping using keyword for HTTP method."""
    s = selector.Selector(parser=lambda x: x + 'p')
    (flexmock(re).should_receive('compile')
                 .once.with_args('/foop')
                 .replace_with(lambda x: x + "c"))
    result = s.add('/foo', GET=33)
    assert result[0] == '/foopc'  # 'pc' as in "parsed and compiled"
    assert result[1].keys() == ['GET']
    assert result[1].values() == [33]
    assert len(s.mappings) == 1


def test_add_dict():
    """Add mapping using dict for HTTP method."""
    s = selector.Selector(parser=lambda x: x + 'p')
    (flexmock(re).should_receive('compile')
                 .once.with_args('/foop')
                 .replace_with(lambda x: x + "c"))
    result = s.add('/foo', method_dict=dict(GET=33))
    assert result[0] == '/foopc'   # 'pc' as in "parsed and compiled"
    assert result[1].keys() == ['GET']
    assert result[1].values() == [33]
    assert len(s.mappings) == 1


def test_add_dict_override():
    """Add mapping using keyword and dict (keyword wins)."""
    s = selector.Selector(parser=lambda x: x + 'p')
    (flexmock(re).should_receive('compile')
                 .once.with_args('/foop')
                 .replace_with(lambda x: x + "c"))
    result = s.add('/foo', method_dict=dict(GET=33), GET=34)
    assert result[0] == '/foopc'  # 'pc' as in "parsed and compiled"
    assert result[1].keys() == ['GET']
    assert result[1].values() == [34]
    assert len(s.mappings) == 1


def test_add_prefix():
    """Add mapping using prefix option."""
    s = selector.Selector(parser=lambda x: x + 'p')
    (flexmock(re).should_receive('compile')
                 .once.with_args('/pre/foop')
                 .replace_with(lambda x: x + "c"))
    assert s.prefix == ''
    result = s.add('/foo', GET=33, prefix='/pre')
    assert s.prefix == ''
    assert result[0] == '/pre/foopc'  # 'pc' as in "parsed and compiled"
    assert result[1].keys() == ['GET']
    assert result[1].values() == [33]
    assert len(s.mappings) == 1


def test_add_wrap():
    """Add mapping using keyword for."""
    s = selector.Selector(parser=lambda x: x + 'p',
                           wrap=lambda x: x + 1)
    (flexmock(re).should_receive('compile')
                 .once.with_args('/foop')
                 .replace_with(lambda x: x + "c"))
    result = s.add('/foo', GET=33)
    assert result[0] == '/foopc'  # 'pc' as in "parsed and compiled"
    assert result[1].keys() == ['GET']
    assert result[1].values() == [34]
    assert len(s.mappings) == 1
