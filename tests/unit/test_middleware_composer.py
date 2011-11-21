"""Unit test `MiddlewareComposer()`."""

import twill

import selector


def test_middleware_composer():
    """Middleware stack should alter return in order.."""

    def make_middleware(txt):
        def middleware(app):
            def wrappedapp(environ, start_response):
                res = app(environ, start_response)
                res.append(txt)
                return res
            return wrappedapp
        return middleware

    # Environ predicates
    t = lambda x: True
    f = lambda x: False
    rules = [(t, make_middleware('a')),
             (f, make_middleware('b')),
             (t, make_middleware('c')),
             (f, make_middleware('d')),
             (t, make_middleware('e'))]

    def app(environ, start_response):
        start_response("200 OK", [('Content-type', 'text/plain')])
        return ["ok "]

    composed = selector.MiddlewareComposer(app, rules)
    twill.add_wsgi_intercept('simple-host', 80, lambda: composed)
    browser = twill.get_browser()
    browser.go('http://simple-host/endpoint')
    assert browser.result.page.startswith("ok eca")
    assert browser.result.http_code == 200
