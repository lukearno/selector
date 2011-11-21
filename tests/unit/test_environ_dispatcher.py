"""Unit test `EnvironDispatcher()`."""

import twill

import selector


def test_environ_dispatcher():
    """Dispatcher chooses an app basen on env."""
    def make_app(name):
        def app(environ, start_response):
            start_response("200 OK", [('Content-type', 'text/plain')])
            return [name]
        return app

    t = lambda env: env['PATH_INFO'] == '/foo'
    f = lambda env: env['PATH_INFO'] == '/bar'
    rules = [(f, make_app('a')),
             (f, make_app('b')),
             (t, make_app('c')),
             (f, make_app('d')),
             (t, make_app('e'))]

    dispatcher = selector.EnvironDispatcher(rules)
    twill.add_wsgi_intercept('simple-host', 80, lambda: dispatcher)
    browser = twill.get_browser()
    browser.go('http://simple-host/foo')
    assert browser.result.page.startswith("c")
    assert browser.result.http_code == 200
