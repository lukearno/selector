"""Py.test plumbing."""

import twill

from selector import Selector


def _twill_selector_browser(id_):
    """Uses host to avoid collisions in the globalness of twill."""
    host = "testhost-%s" % id_
    s = Selector()
    twill.add_wsgi_intercept(host, 80, lambda: s)
    b = twill.get_browser()

    def go(path):
        b.go('http://%s%s' % (host, path))
        headers = b._browser._response._headers.headers
        print s
        return (b.result.http_code,
                headers,
                b.result.page)

    return  dict(selector=s, browser=b, go=go)


def generate_twill_selector_browsers():
    """Get selector, browser and go function for tests.

    Comes in a dict for funcargs.
    Feeds methods with signature `(selector, browser, go)`.
    """
    for i in range(100):
        yield _twill_selector_browser(i)


twill_selector_browsers = generate_twill_selector_browsers()


def pytest_generate_tests(metafunc):
    """Populate test arguments."""
    if 'selector' in metafunc.funcargnames:
        # Expects signature to be (s, b, go)
        metafunc.addcall(funcargs=twill_selector_browsers.next())
