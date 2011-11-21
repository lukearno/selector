"""Test the default handlers for 404s and 405s."""

from selector import method_not_allowed, not_found
import twill


def test_not_found():
    """The "not found" handler return a 404."""
    twill.add_wsgi_intercept('not-found-host', 80, lambda: not_found)
    browser = twill.get_browser()
    browser.go('http://not-found-host/')
    assert browser.result.page.startswith("404 Not Found")
    assert browser.result.http_code == 404


def test_method_not_allowed():
    """The "method not allowed" handler return a 405."""
    def app(environ, start_response):
        environ['selector.methods'] = ['GET', 'PUT']
        return method_not_allowed(environ, start_response)
    twill.add_wsgi_intercept('not-found-host', 80, lambda: app)
    browser = twill.get_browser()
    browser.go('http://not-found-host/')
    assert browser.result.page.startswith("405 Method Not Allowed")
    assert browser.result.http_code == 405
