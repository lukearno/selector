"""Unit test naked object stuff."""

from flexmock import flexmock

import selector


class NakedMock(selector.Naked):
    """Base class for classes for testing `Naked`."""

    def tell(self, name):
        """For replacement by flexmock.

        It looks like flexmock breaks the expose decorator,
        so use `tell` to get around mocking exposed methods.
        """

    @selector.expose
    def index(self, environ, start_response):
        self.tell('index')

    def _not_found(self, environ, start_response):
        self.tell('_not_found')


class NotNestable(NakedMock):
    """Not nestable and only index exposed."""

    _expose_all = False
    _exposed = False


class AllExposed(NakedMock):
    """Totally exposed and nestable."""

    _expose_all = True

    def info(self, environ, start_response):
        self.tell('info')

    def nonsecrets(self, environ, start_response):
        self.tell('nonsecrets')


class SomeExposed(NakedMock):
    """Selectively exposed."""

    _expose_all = False

    # For testing nesting...
    not_nestable = NotNestable()
    nestable = AllExposed()

    @selector.expose
    def info(self, environ, start_response):
        self.tell('info')

    def secrets(self, environ, start_response):
        self.tell('secrets')


def test_expose():
    """Mark a callable as "exposed"."""
    class Obj(object):
        pass
    o = Obj()
    selector.expose(o)
    assert o._exposed


def test_exposure():
    """Method is exposed by decorator."""
    some_exposed = SomeExposed()
    all_exposed = AllExposed()
    not_nestable = NotNestable()
    # Methods are exposed or not as we expected.
    assert some_exposed._is_exposed(some_exposed.info)
    assert not some_exposed._is_exposed(some_exposed.secrets)
    assert all_exposed._is_exposed(all_exposed.info)
    assert all_exposed._is_exposed(all_exposed.nonsecrets)
    assert not not_nestable._is_exposed(all_exposed.info)
    # Nestables are exposed, non-nestables are not
    assert all_exposed._is_exposed(all_exposed)
    assert some_exposed._is_exposed(some_exposed)
    assert not not_nestable._is_exposed(not_nestable)


def naked_test_call(NakedClass,
                    script_name_before,
                    path_info_before,
                    callable_name,
                    script_name_after,
                    path_info_after):

    def generated_test():
        environ = dict(
            SCRIPT_NAME=script_name_before,
            PATH_INFO=path_info_before
        )
        naked = NakedClass()
        (flexmock(naked)
            .should_receive('tell')
            .with_args(callable_name)
            .once
            .replace_with(lambda y: None))
        naked(environ, None)
        assert environ['SCRIPT_NAME'] == script_name_after
        assert environ['PATH_INFO'] == path_info_after

    return generated_test


test_call_index_slash = naked_test_call(
    AllExposed,
    '/foo/bar',
    '/',
    'index',
    '/foo/bar/',
    '')


test_call_index_noslash = naked_test_call(
    AllExposed,
    '/foo/bar',
    '',
    'index',
    '/foo/bar',
    '')


test_call_index_slash_on_script_name = naked_test_call(
    AllExposed,
    '/foo/bar/',
    '',
    'index',
    '/foo/bar/',
    '')


test_call_an_implicitly_exposed_method = naked_test_call(
    AllExposed,
    '/foo/bar',
    '/info/remainder',
    'info',
    '/foo/bar/info',
    '/remainder')


test_call_an_explicitly_exposed_method = naked_test_call(
    SomeExposed,
    '/foo/bar',
    '/info/remainder',
    'info',
    '/foo/bar/info',
    '/remainder')


test_call_an_unexposed_method = naked_test_call(
    SomeExposed,
    '/foo/bar',
    '/secrets',
    '_not_found',
    '/foo/bar',
    '/secrets')


def test_call_a_nested_unnestable():
    environ = dict(
        SCRIPT_NAME='/foo/bar',
        PATH_INFO='/nestable/info'
    )
    some_exposed = SomeExposed()
    (flexmock(some_exposed.nestable)
        .should_receive('tell')
        .with_args('info')
        .once
        .replace_with(lambda y: None))
    some_exposed(environ, None)
    assert environ['SCRIPT_NAME'] == '/foo/bar/nestable/info'
    assert environ['PATH_INFO'] == ''


test_call_ = naked_test_call(
    SomeExposed,
    '/foo/bar',
    '/unnestable/info',
    '_not_found',
    '/foo/bar',
    '/unnestable/info')


def test_notfound():
    """Not found is tested elsewhere."""
    assert selector.Naked._not_found is selector.not_found
