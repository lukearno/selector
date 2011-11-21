"""Unit test `Selector.slurp()`."""

from flexmock import flexmock

import selector

from . import mocks


def test_slurp_no_mayo():
    """Just slurp up some mappings in a list."""
    s = selector.Selector()
    flexmock(s).should_receive('add').times(2)
    s.slurp(mocks.slurpables)


def test_slurp_the_works():
    """Slurp with prefix, parser and wrap."""
    myparser = lambda x: x
    mywrap = lambda x: x
    s = selector.Selector()
    assert s.prefix == ''
    assert s.parser.__class__ == selector.SimpleParser
    assert s.wrap is None
    flexmock(s).should_receive('add').times(2).replace_with(
        mocks.checkadd(s, '/pre', myparser, mywrap))
    s.slurp(mocks.slurpables, prefix='/pre', parser=myparser, wrap=mywrap)
    assert s.prefix == ''
    assert s.parser.__class__ == selector.SimpleParser
    assert s.wrap is None
