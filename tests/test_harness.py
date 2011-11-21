"""Just verify that the test harness itself is working."""

from flexmock import flexmock

from .unit import mocks


def test_harness():
    """This is a do-nothing test to verify the harness itself."""
    assert 1 == 1


def test_mock_open():
    """Test mock for builtin `open()`."""
    mocks.mock_open('test_mock_open', ['a', 'b', 'c'], 'rb')
    m = flexmock(calls=lambda x: x)
    m.should_receive('calls').times(3)
    with open('test_mock_open', 'rb') as foofile:
        for line in foofile:
            m.calls(line)
        for line in foofile:
            m.calls("Again %s" % line)
