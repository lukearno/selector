# Selector

WSGI request delegation. (AKA routing.)

```bash
$ pip install selector
```

## Overview

This distribution provides WSGI middleware
for "RESTful" dispatch of requests to WSGI applications
by URL path and HTTP request method.
Selector now also comes with components for environ-based
dispatch and on-the-fly middleware composition.
There is a very simple optional mini-language for
path matching expressions. Alternately we can easily use
regular expressions directly or even create our own
mini-language. There is a simple "mapping file" format
that can be used. There are no architecture specific
features (to MVC or whatever). Neither are there any
framework specific features.

## Quick Start

```python
import selector

app = selector.Selector()
app.add('/resource/{id}', GET=wsgi_handler)
```

If you have ever designed a REST protocol you have probably made a table that
looks something like this:

| `/foos/{id}`  |                                   |
| ------------- | --------------------------------- |
| `POST`        | Create a new foo with id == {id}. |
| `GET`         | Retrieve the foo with id == {id}. |
| `PUT`         | Update the foo with id == {id}.   |
| `DELETE`      | Delete the foo with id == {id}.   |
 
Selector was designed to fit mappings of this kind.

Lets suppose that we are creating a very simple app. The only requirement is
that `http://example.com/myapp/hello/Guido` responds with a simple page that 
says hello to Guido (where "Guido" can actually be any name at all). 
The interface of this extremely useful service looks like:

| `/myapp/hello/{name}` |                       |
| --------------------- | --------------------- |
| `GET`                 | Say hello to {name}.  |

Here's the code for `myapp.py`:

```python
from selector import Selector

def say_hello(environ, start_response):
    args, kwargs = environ['wsgiorg.routing_args']
    start_response("200 OK", [('Content-type', 'text/plain')])
    return ["Hello, %s!" % kwargs['name']]
    
app = Selector()
app.add('/myapp/hello/{name}', GET=say_hello)
```

Run it with [Green Unicorn](http://gunicorn.org/):

```bash
$ gunicorn myapp:app
```

Of course, you can use Selector in any WSGI environment.

## How It Works

When a route is added, the **path expression** is converted into a regular
expression. (You can also use regexes directly.) When the `Selector` 
instance receives a request, it checks each regex until a
match is found. If no match is found, the request is passed to
`Selector.status404`. Otherwise, it modifies the `environ` to store some 
information about the match and looks up the `dict` of HTTP request methods 
associated with the regex. If the HTTP method is not found in the `dict`,
the request is passed to `Selector.status405`. Otherwise,
the request is passed to the WSGI handler associated with the HTTP method.

## Path Expressions

As you probably noticed, you can capture  named portions of the path into 
`environ['wsgiorg.routing_args']`. (They also get put into 
~~`environ['selector.vars']`~~, but that is *deprecated* in favor of a 
[routing args standard](http://www.wsgi.org/en/latest/specifications/routing_args.html).)

You can also capture things positionally:.

```python
def show_tag(environ, start_response):
    args, kwargs = environ['wsgiorg.routing_args']
    user = kwargs['user']
    tag = args[0]
    # ...

s.add('/myapp/{user}/tags/{}', GET=show_tag)
```

Selector supports a number of datatypes for your routing args, specified
like this: `{VARNAME:DATATYPE}` or just `{:DATATYPE}`.

| type      | regex       |
| --------- | ----------- |
| `word`    | `\w+`       |  
| `alpha`   | `[a-zA-Z]+` |
| `digits`  | `\d+`       |
| `number`  | `\d*.?\d+`  | 
| `chunk`   | `[^/^.]+`   |
| `segment` | `[^/]+`     |
| `any`     | `.+`        |

These types work for both named and positional routing args:

```python
s.add('/collection/{:digits}/{docname:chunk}.{filetype:chunk}', GET=foo)
```

(You can even add your own types with just a name and a regex,
but we will get to that in a moment.)

Parts of the URL path can also be made optional using `[`square brackets.`]`

```python
s.add("/required-part[/optional-part]", GET=any_wsgi)
```

Optional portions in path expressions can be nested.

```python
s.add("/recent-articles[/{topic}[/{subtopic}]][/]", GET=recent_articles)
```

By default, selector does **path consumption**, which means the matched portion
of the path information is moved from `environ['PATH_INFO']` to 
`environ['SCRIPT_NAME']` when routing a request.
The matched portion of the path is also appended to a list found or created 
in `environ['selector.matches']`, where it is is available
to upstack consumers.
It's useful in conjunction with open ended path expressions
(using the pipe character, `|`) for recursive dispatch:

```python
def load_book(environ, start_response):
    args, kwargs = environ['wsgiorg.routing_args']
    # load book
    environ['com.example.book'] = db.get_book(kwargs['book_id'])
    return s(environ, start_response)

def load_chapter(environ, start_response):
    book = environ['com.example.book']
    args, kwargs = environ['wsgiorg.routing_args']
    chapter = book.chapters[kwargs['chapter_id'])
    # ... send some response

s.add("/book/{book_id}|", GET=load_book)
s.add("/chapter/{chapter_id}", GET=load_chapter)
```

## Plain Regexes, Custom Types and Custom Parsers

You can create your own parser and your own path expression 
syntax, or use none at all. All you need is a callable that
takes the path expression and returns a regex string.

```python
s.parser = lambda x: x
s.add('^\/somepath\/$', GET=foo)
```

You can add a custom type to the default parser when you instantiate
it or by modifying it in place.

```python
parser = selector.SimpleParser(patterns={'mytype': 'MYREGEX'})
assert parser('/{foo:mytype}') == r'^\/(?P<foo>MYREGEX)$'
```

```python
s.parser.patterns['othertype'] = 'OTHERREGEX'
assert parser('/{foo:othertype}') == r'^\/(?P<foo>OTHERREGEX)$'
```

## Prefix and Wrap

Often you have some common prefix you would like appended to your
path expressions automatically when you add routes. 
You can set that when instantiating selector and change it as you
go. 

```python
# Add the same page under three prefixes:
s = Selector(prefix='/myapp')
s.add('/somepage', GET=get_page)
s.prefix = '/otherapp'
s.add('/somepage', GET=get_page)
s.add('/somepage', GET=get_page, prefix='/app3')
```

Selector can automatically wrap the callables you route to.
I often use [Yaro](http://lukearno.com/projects/yaro), 
which puts WSGI behind a pretty request object.

```python
import selector, yaro  
  
def say_hello(req):  
    return "Hello, World!"  
  
s = selector.Selector(wrap=yaro.Yaro)  
s.add('/hello', GET=say_hello) 
```

## Adding Routes

There are basically three ways to add routes.

### One at a Time

So far we have been adding routes with `.add()`

```python
foo_handlers = {'GET': get_foo, 'POST': create_foo}

s.add('/foo', method_dict=foo_handlers)
s.add('/bar', GET=bar_handler)
s.add('/read-only-foo',
      method_dict=foo_handlers,
      POST=sorry_charlie)
)
```

Notice how `POST` was overridden for `/read-only-foo`.

`.add()` also takes a `prefix` key word arg.

### Slurping up a List

`.slurp()` will load mapping from a list of tuples, which turns out
to be pretty ugly, so you would probably only do this if you were building
the list programmatically. (... like, if parsing your own URL mapping file
format, for instance.)

```python
routes = [('/foo', {'GET': foo}),
          ('/bar', {'GET': bar})]
s = Selector(mappings=routes)
# or
s.slurp(routes)
```

`.slurp()` takes the keyword args `prefix`, `parser` and `wrap`...

### Mapping Files

Selector supports a sweet URL mapping file format.

```
/foo/{id}[/]  
    GET somemodule:some_wsgi_app  
    POST pak.subpak.mod:other_wsgi_app  
  
@prefix /myapp  
@wrap yaro:Yaro

/path[/]  
    GET module:app  
    POST package.module:get_app('foo')  
    PUT package.module:FooApp('hello', resolve('module:setting'))  
  
@parser :lambda x: x  
@wrap :lambda x: x  

@prefix  
^/spam/eggs[/]$  
    GET mod:regex_mapped_app
```

This format is read line by line. 

* Blank lines and lines starting with `#` as their first 
  non-whitespace characters are ignored. 
* Directives start with `@`
  and modulate route adding behavior.
* Path expressions come on their own line and
  have no leading whitespace
* HTTP method -> handler mappings are indented

There are three directives: `@prefix`, `@parser` and `@wrap`, 
and they do what you think they do. 
The `@parser` and `@wrap` directives take
[resolver](http://lukearno.com/projects/resolver/)
statements. 
Handlers are resolver statements too.
HTTP method to handler mappings are applied to the preceding 
path expression.

Files of this format can be used in the following ways.

```python
s = Selector(mapfile='map1.urls')
s.slurp_file('map2.urls')
```

`Selector.slurp_file()` supports optional `prefix`, `parser` and `wrap`
keyword arguments, too.

## Initializing a Selector

All the functionality is covered above, but, to summarize the init
signature:

```python
    def __init__(self,
                 mappings=None,
                 prefix="",
                 parser=None,
                 wrap=None,
                 mapfile=None,
                 consume_path=True):
```

## Customizing 404s and 405s and Chain Dispatchers

You can replace Selector's 404 and 405 handlers. They're just WSGI.

```python
s = Selector()
s.status404 = my_404_wsgi
s.status405 = my_405_wsgi
```

You could chain Selector instances together, or fall through to other
types of dispachers or any handler at all really.

```python
s1 = Selector(mapfile='map1.urls')
s2 = Selector(mapfile='map2.urls')
s1.status404 = s2
```

## Environ Dispatcher

`EnvironDispatcher` routes a request based on the `environ`. It's 
instantiated with a list of `(predicate, wsgi_app)` pairs. Each predicate is a
callable that takes one argument (`environ`) and returns True or False. When
called, the instance iterates through the pairs until it finds a predicate that
returns True and runs the app paired with it.

```python
is_admin = lambda env: 'admin' in env['session']['roles'] 
is_user = lambda env: 'user' in env['session']['roles'] 
default = lambda env: True

rules = [(is_admin, admin_screen), (is_user, user_screen), (default,
access_denied)]

envdis = EnvironDispatcher(rules)

s = Selector()
s.add('/user-info/{username}[/]', GET=envdis)
```

## Middleware Composer

Another WSGI middleware included in selector allows us compose middleware on
the fly (compose as in function composition) in a similar way.
`MiddlewareComposer` also is instantiated with a list of rules, only instead 
of WSGI apps you have WSGI middleware. When called, the instance applies all 
the middlewares whose predicates are true for environ in reverse order, and 
calls the resulting app.

```python
lambda x: True; f = lambda x: False
rules = [(t, a), (f, b), (t, c), (f, d), (t, e)]
                
composed = MiddlewareComposer(app, rules)

s = Selector()
s.add('/endpoint[/]', GET=composed)
```

is equivalent to 

```python
a(c(e(app)))
```

## Routing Args in Callable Signatures

There are some experimental, somewhat old decorators in Selector
that facilitate putting your routing args into the signatures
of your callables.

```python
from selector import pliant, opliant  
  
@pliant  
def app(environ, start_response, arg1, arg2, foo='bar'):  
    ...  
  
class App(object):  
    @opliant  
    def __call__(self, environ, start_response, arg1, arg2, foo='bar'):  
        ...  
```

## Exposing Callables

Selector now provides classes for naked object and HTTP method to object method
based dispatch, for completeness.

```python
from selector import expose, Naked, ByMethod  
  
class Nude(Naked):  
    # If this were True we would not need expose  
    _expose_all = False  
      
    @expose  
    list(self, environ, start_response):  
        ...  
  
class Methodical(ByMethod):  
    def GET(self, environ, start_response):  
        ...  
    def POST(self, environ, start_response):  
        ...
```

## API Docs

Read [Selector's API Docs](http://readthedocs.org/docs/selector/)
on [Read the Docs](http://readthedocs.org/).

## Tests

Selector has 100% unit test coverage, as well as some basic functional tests.

Here is output from a recent run.

```bash
luke$ fab test
[localhost] local: which python
Running unit tests with coverage...
[localhost] local: py.test -x --doctest-modules selector.py --cov selector
tests/
===============================================================================
test session starts
===============================================================================
platform darwin -- Python 2.6.1 -- pytest-2.1.3
collected 72 items 

selector.py .
tests/__init__.py .
tests/test_harness.py ...
tests/util.py .
tests/wsgiapps.py .
tests/functional/__init__.py .
tests/functional/conftest.py .
tests/functional/test_simple_routes.py .....
tests/unit/__init__.py .
tests/unit/mocks.py .
tests/unit/test_by_method.py ....
tests/unit/test_default_handlers.py ...
tests/unit/test_environ_dispatcher.py ..
tests/unit/test_middleware_composer.py ..
tests/unit/test_naked.py ............
tests/unit/test_pliant.py ...
tests/unit/test_selector_add.py ......
tests/unit/test_selector_call.py ..
tests/unit/test_selector_init.py ...
tests/unit/test_selector_mapping_format.py .......
tests/unit/test_selector_select.py .....
tests/unit/test_selector_slurp.py ...
tests/unit/test_simple_parser.py ....
----------------------------------------------------------------- coverage:
platform darwin, python 2.6.1-final-0
-----------------------------------------------------------------
Name       Stmts   Miss  Cover
------------------------------
selector     261      0   100%

============================================================================ 72
passed in 1.13 seconds
============================================================================
[localhost] local: which python
Running PEP8 checker
No PEP8 violations found! W00t!
```

## Release Management Policy and Versioning

Selector is [SemVer](http://semver.org/) compliant.

Release management is codified in the `fabfile.py` in the `release` task.

## Hack!

Fork it. 

```bash
$ git clone http://github.com/lukearno/selector.git
```

Set yourself up in a virtualenv and list the fab tasks
at your disposal.
(Requires [Virtualenv](http://pypi.python.org/pypi/virtualenv).)

```bash
$ . bootstrap
```

Run the tests.

```bash
(.virt/)$ fab test
```

## Licenses

Use under MIT or GPL.

Copyright (c) 2006 Luke Arno, http://lukearno.com/
