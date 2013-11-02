"""setup - setuptools based setup for selector"""

from setuptools import setup


with open('VERSION', 'r') as version_file:
    version = version_file.read().strip()

setup(name='selector',
      version=version,
      description='WSGI request delegation. (AKA routing.)',
      long_description=" ".join("""
        This distribution provides WSGI middleware
        for "RESTful" mapping of URL paths to WSGI applications.
        Selector now also comes with components for environ based
        dispatch and on-the-fly middleware composition.
        There is a very simple optional mini-language for
        path expressions. Alternately we can easily use
        regular expressions directly or even create our own
        mini-language. There is a simple "mapping file" format
        that can be used. There are no architecture specific
        features (to MVC or whatever). Neither are there any
        framework specific features.""".split()),
      author='Luke Arno',
      author_email='luke.arno@gmail.com',
      url='http://github.com/lukearno/selector/',
      license="MIT",
      py_modules=['selector'],
      packages=[],
      install_requires=['resolver'],
      keywords="wsgi delegation routing web http rest webapps",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities'])
