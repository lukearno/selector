"""Unit Test `SimpleParser()`."""

import csv

import pytest

import selector


def test_parser_expectations():
    """Just a basic test of the builtin parser."""
    parser = selector.SimpleParser()
    with open('tests/unit/path-expression-expectations.csv', 'r') as pex:
        reader = csv.reader(pex)
        for pe, re in reader:
            print pe
            assert parser(pe) == re


def test_parser_raises_exception():
    """Malformed path expression raises error."""
    parser = selector.SimpleParser()
    with pytest.raises(selector.PathExpressionParserError):
        parser("/this/is/a/[broken/path/expression")


def test_parser_with_custom_type():
    """Custom types can be provided to the parser or modifying .patterns."""
    parser = selector.SimpleParser(patterns={'mytype': 'MYREGEX'})
    assert parser('/{foo:mytype}') == r'^\/(?P<foo>MYREGEX)$'
    parser.patterns['othertype'] = 'OTHERREGEX'
    assert parser('/{foo:othertype}') == r'^\/(?P<foo>OTHERREGEX)$'
