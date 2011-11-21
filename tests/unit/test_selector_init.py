"""Unit test `Selector()` instantiation."""

from flexmock import flexmock

import selector

from . import mocks


def test_instantiate_selector_args():
    """Instantiate a `Selector()` with the works."""
    myparser = lambda x: x
    mywrap = lambda x: x + 1
    (flexmock(selector.Selector).should_receive('slurp')
                                .with_args(mocks.slurpables)
                                .once.ordered)
    (flexmock(selector.Selector).should_receive('slurp_file')
                                .with_args('some.urls')
                                .once.ordered)
    s = selector.Selector(
        mappings=mocks.slurpables,
        prefix='/aprefix',
        parser=myparser,
        wrap=mywrap,
        mapfile='some.urls',
        consume_path=False)
    assert s.prefix == '/aprefix'
    assert s.parser is myparser
    assert s.wrap is mywrap
    assert s.consume_path is False


def test_instantiate_selector_defaults():
    """Instantiate a `Selector()`, hold-the-mayo please."""
    s = selector.Selector()
    s.mappings = []
    s.prefix is None
    s.parser.__class__ is selector.SimpleParser
    s.wrap is None
    s.consume_path is True
