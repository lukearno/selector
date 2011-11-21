"""Mock object support for unit tests."""

import sys

from flexmock import flexmock


def mock_open(filename, lines, mode='rb'):
    """An open() call for filename returns lines."""
    mock = flexmock(sys.modules['__builtin__'])
    mock.should_call('open')  # set the fall-through
    mock.should_receive('open').with_args(filename, mode).and_return(
        flexmock(__enter__=lambda: lines.__iter__(),
                 __exit__=lambda x, y, z: None))


def mock_regex(matched=None, groupdict={}):
    """Mocks a regex, of course.

    If you give it `matched`, it will claimed to have matched what you passed
    it and to have extracted named groups according to `groupdict`. Otherwise
    it will claim to have failed.
    """
    if matched:
        match = flexmock(groupdict=lambda: groupdict,
                         group=lambda x: matched)
    else:
        match = None
    return flexmock(search=lambda x: match)


slurpables = [
    ('/and-one', dict(GET=11)),
    ('/and-two', dict(GET=22)),
]


def checkadd(s, prefix, parser, wrap):
    def myadd(a, method_dict=None):
        print a, method_dict
        assert s.prefix == prefix
        assert s.parser == parser
        assert s.wrap == wrap
    return myadd
