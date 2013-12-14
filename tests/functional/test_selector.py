"""Functional tests for `Selector()`."""

from webob import Request, Response
from .wsgiapps import say_hello, here_i_am, say_hello_positional


def test_simple_route(selector, browser, go):
    """Call the hello app.."""
    selector.add('/myapp/hello/{name}', GET=say_hello)
    code, headers, page = go('/myapp/hello/Guido')
    assert code == 200
    assert page.startswith("Hello Guido!")


def test_simple_route_positional(selector, browser, go):
    """Call the hello app with positional arg in path."""
    selector.add('/myapp/hello/{}', GET=say_hello_positional)
    code, headers, page = go('/myapp/hello/Guido')
    assert code == 200
    assert page.startswith("Hello Guido!")


def tesiiit_custom_parser(selector, browser, go):
    """Use a plain regex with a do-nothing parser."""
    orig = selector.parser
    selector.parser = lambda x: x
    selector.add(r'^\/here-i-am$', GET=here_i_am)
    selector.parser = orig
    code, headers, page = go('/here-i-am')
    assert code == 200
    assert page.startswith("Here I am.")


def test_404_and_405(selector, browser, go):
    """Selector responds with 404s and 405s appropriately."""
    selector.add('/post-only', POST=here_i_am)
    code, headers, page = go('/doesnt-exist')
    assert code == 404
    assert page.startswith("404 Not Found")
    code, headers, page = go('/post-only')
    assert code == 405
    assert page.startswith("405 Method Not Allowed")
    assert "Allow: POST\n" in list(headers)


def test_seperate_http_method_paths(selector, browser, go):
    selector.add('/ws/hello', GET=here_i_am)
    selector.add('/ws/{slug}', POST=here_i_am)

    request = Request.blank('/ws/hello', method='GET')
    response = request.send (selector)

    assert response.status_code == 200
    assert response.body.startswith("Here I am.")

    request = Request.blank('/ws/hello', method='POST')
    response = request.send (selector)

    assert response.status_code == 200
    assert response.body.startswith("Here I am.")


