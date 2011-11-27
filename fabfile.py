"""Project automation for Selector.

fab -l       - list available tasks
fab -d TASK  - describe a task in detail
"""

import contextlib
import csv
import sys

from os.path import abspath as _abspath

import pkg_resources

from fabric.api import local, puts, settings, hide, abort, lcd, prefix
from fabric import colors as c
from fabric.contrib.console import confirm


import selector


def _invirt():
    """Make sure we have bootstrapped."""
    with settings(hide('running', 'stdout', 'stderr')):
        current_py = local('which python', capture=True)
        virt_py = _abspath('.virt/bin/python')
        if not current_py == virt_py:
            puts(c.red('Not in virtualenv! Please run ". bootstrap".'))
            sys.exit(1)


def pep8():
    """Check for pep8 style compliance."""
    _invirt()
    puts(c.magenta("Running PEP8 style checker..."))
    with settings(hide('warnings', 'stdout', 'stderr', 'running'),
                  warn_only=True):
        violations = local('pep8 *.py */*.py */*/*.py', capture=True)
        if violations.strip():
            violations_count = len(violations.split('\n'))
            puts(c.red("%s PEP8 violations! Oh nooooes!" % violations_count))
            puts(c.cyan(violations))
        else:
            violations_count = 0
            puts(c.green("No PEP8 violations found! W00t!"))
    return violations_count


def pyflakes():
    """Check for pyflakes warnings."""
    _invirt()
    puts(c.magenta("Running PyFlakes style checker..."))
    with settings(hide('warnings', 'stdout', 'stderr', 'running'),
                  warn_only=True):
        warnings = local('pyflakes *.py */*.py */*/*.py', capture=True)
        if warnings.strip():
            warnings_count = len(warnings.split('\n'))
            puts(c.red("%s Pyflakes warningss! Oh nooooes!" % warnings_count))
            puts(c.cyan(warnings))
        else:
            warnings_count = 0
            puts(c.green("No Pyflakes warnings! W00t!"))
    return warnings_count


def stylechecks():
    """Do all style checks and abort if there are warnings."""
    if pep8() or pyflakes():
        abort(c.red("Style checks failed!"))


def test():
    """Run the all tests and show coverage."""
    _invirt()
    puts(c.magenta("Running unit tests with coverage..."))
    local('py.test -x'
                 ' --doctest-modules selector.py'
                 ' --cov selector'
                 ' tests/')
    stylechecks()


def html_coverage():
    """Run the all tests and write HTML coverage report."""
    _invirt()
    puts(c.magenta("Running unit tests with coverage..."))
    local('py.test -x'
                 ' --doctest-modules selector.py'
                 ' --cov selector'
                 ' --cov-report=html'
                 ' tests/')
    stylechecks()


def unittest():
    """Run the unit tests only, with coverage."""
    _invirt()
    puts(c.magenta("Running unit tests with coverage..."))
    local('py.test -x'
                 ' --doctest-modules selector.py'
                 ' --cov selector'
                 #' --cov-report=html'
                 ' tests/unit')
    stylechecks()


def autotest():
    """Run all tests with coverage and junit XML output."""
    _invirt()
    puts(c.magenta("Running tests with coverage"))
    with settings(hide('running', 'stdout')):
        local('mkdir -p build/')
    local('py.test --junitxml build/junit.xml'
                 ' --doctest-modules selector.py'
                 ' --cov-report xml'
                 ' --cov selector tests/')
    violations_count = pep8()
    puts(c.blue("Writing count to build/pep8-violations.txt"))
    with settings(hide('running')):
        local("echo %s > build/pep8-violations.txt" % violations_count)
    warnings_count = pyflakes()
    puts(c.blue("Writing count to build/pyflakes-warnings.txt"))
    with settings(hide('running')):
        local("echo %s > build/pyflakes-warnings.txt" % warnings_count)
    if violations_count or warnings_count:
        abort(c.red("Style check failed!"))


@contextlib.contextmanager
def _freshvirt(virt):
    puts(virt)
    local('rm -rf %s' % virt)
    local('virtualenv --no-site-packages --distribute %s' % virt)
    with prefix('. %s/bin/activate' % virt):
        with settings(hide('stdout', 'stderr', 'warnings', 'running'),
                      warn_only=True):
            result = local('python -c "import selector"')
            if result.return_code != 1:
                abort(c.red("Failed to create clean virt without selector."))
        yield


def buildtest():
    """Try installing from egg and importing in a clean virt.

    Does `pip` and `easy_install`.
    """
    puts(c.blue("Running build/install test..."))
    with _freshvirt('.buildtest'):
        version = local('cat VERSION', capture=True)
        local('rm -rf dist/*')
        local('python setup.py sdist bdist_egg')
        local('easy_install dist/selector-%s.tar.gz' % version)
        local('python -c "import selector"')
    puts(c.magenta("Built and installed successfully"))


def post_release_install_verification():
    """Try installing from pypi and importing in a clean virt.

    Does `pip` and `easy_install`.
    """
    puts(c.blue("Running post-release install verification..."))
    with _freshvirt('.buildtest'):
        local('pip install selector')
        local('python -c "import selector"')
    with _freshvirt('.buildtest'):
        local('easy_install selector')
        local('python -c "import selector"')
    puts(c.magenta("Release verification successful!"))


def devdeps():
    """Install the development dependencies.."""
    _invirt()
    puts(c.magenta("Installing dev dependencies..."))
    with settings(hide('stdout')):
        local('pip install -r dev-req.txt')


def regenerate_api_docs():
    """Regenerate the generated API docs with sphynx."""
    if confirm('Are you sure you want to overwrite .rst files?'):
        puts(c.red("Regenerating .rst files with sphinx-apidoc..."))
        with settings(hide('running', 'stdout')):
            local('sphinx-apidoc -f -o docs/ . setup.py')
            local('rm -f docs/modules.rst')
            local('rm -f docs/setup.rst')
            local('rm -f docs/fabfile.rst')
            local('rm -f docs/tests.rst')
            local('rm -f docs/tests.functional.rst')
            local('rm -f docs/tests.unit.rst')


def regenerate_expectations():
    """Regenerate the expections for the SimpleParser unit tests."""
    if not confirm(c.red('Are you _really_ sure you have a working parser??')):
        abort(c.blue("Ok, check that out and come back when you are sure."))
    parser = selector.SimpleParser()
    with open('tests/unit/path-expressions.csv', 'r') as expressions:
        with open('tests/unit/path-expression-expectations.csv', 'w') as out:
            reader = csv.reader(expressions)
            writer = csv.writer(out)
            for (pathexpression,) in reader:
                writer.writerow([pathexpression, parser(pathexpression)])


def build_api_docs():
    """Build the HTML API docs."""
    puts(c.magenta("Building HTML API docs..."))
    with settings(hide('running', 'stdout', 'stderr')):
        with lcd('docs'):
            local('make html')


def clean(deep=False):
    """Kill the virtual env and all files generated by build and test.

    [:deep=False]

    If deep is True, removes the virtualenv and all.
    """
    _invirt()
    if confirm('This will delete stuff. You sure?'):
        puts(c.red("Cleaning up..."))
        with settings(hide('running', 'stdout')):
            local('rm -rf build/')
            local('rm -f coverage.xml')
            local('rm -rf selector.egg-*')
            local('rm -rf *.pyc')
            local('rm -rf __pycache__/')
            local('rm -rf tests/__pycache__/')
            local('rm -rf tests/*.pyc')
            local('rm -rf tests/*/__pycache__/')
            local('rm -rf tests/*/*.pyc')
            local('rm -rf htmlcov')
            with lcd('docs'):
                local('make clean')
            if deep:
                puts(c.red("Removing virtualenv .virt/"))
                puts(c.red("You will need to `. bootstrap` again."))
                local('rm -rf .virt/')
    else:
        puts(c.red("Not cleaning."))


def _abort_if_not_valid_release_type(release_type):
    """Make sure we have a valid release type."""
    release_type = release_type.lower()
    if release_type not in ("major", "minor", "patch"):
        abort(c.red("Not a valid release type, see `fab -d release`"))
    return release_type


def compute_version(release_type, rc=False):
    """Compute a semver compliant version number.

    :release_type[,rc=False]

    Release types:  MAJOR - non-backwards compatible feature(s)
                    MINOR - backwards compatible feature(s) addition
                    PATCH - backwards compatible bug fix(es)
    "rc" indicates a Release Candidate.
    """
    # Make sure it is a valid type of release.
    release_type = _abort_if_not_valid_release_type(release_type)
    # Find the latest version.
    tags = (t.strip() for t in local('git tag', capture=True).split('\n'))
    versions = [t[1:] for t in tags if t.startswith('v')]
    versions.sort(key=pkg_resources.parse_version)
    final_versions = [v for v in versions if 'rc' not in v]
    latest_final = final_versions and final_versions[-1] or '0.0.0'
    # Bump the version number.
    major, minor, patch = map(int, latest_final.split('.'))
    if release_type == 'major':
        major += 1
        minor = 0
        patch = 0
    if release_type == 'minor':
        minor += 1
        patch = 0
    if release_type == 'patch':
        patch += 1
    new_version = ".".join(map(str, [major, minor, patch]))
    # Append a release candidate number to the version?
    if rc:
        candidate_number = 0
        while 1:
            candidate_number += 1
            candidate_version = "%src%s" % (new_version, candidate_number)
            if candidate_version not in versions:
                break
        new_version = candidate_version

    puts(c.magenta("Calculated version: %s" % new_version))
    return new_version


def _sync_and_preflight_check(branch, release_type):
    """Sync up repository and check that things are in order for release."""
    # Sync.
    puts(c.blue("Git fetching origin..."))
    local("git fetch origin",  capture=True)
    puts(c.blue("Running preflight checks..."))
    # Make release type is valid.
    _abort_if_not_valid_release_type(release_type)
    # Make sure we don't have any outstanding edits hanging around.
    if (local("git diff",  capture=True).strip()
        or local("git status -s", capture=True)):
        abort(c.red("It seems you have unstaged local changes."))
    if local("git diff --staged",  capture=True).strip():
        abort(c.red("It seems you have changes in the staging area."))
    # Local master and origin/master must be up-to-date with each other.
    if (local("git diff origin/master...master", capture=True).strip()
         or local("git diff master...origin/master", capture=True).strip()):
        abort(c.red("master is out of sync with origin!."))
    # Local branch and origin/branch must be up-to-date with each other.
    if (local("git diff origin/%s...%s" % (branch, branch),
              capture=True).strip()
         or local("git diff %s...origin/%s" % (branch, branch),
                  capture=True).strip()):
        abort(c.red("master is out of sync with origin!."))
    # Make sure our branch has all the latest from master.
    changes_from_master = local("git diff %s...master" % branch, capture=True)
    if changes_from_master:
        abort(c.red("%s is out of sync with master and needs to be merged."))
    # See what changes are in the branch and make sure there is something to
    # release.
    changes = local("git diff master...%s" % branch, capture=True)
    if not changes:
        abort(c.red("No changes there to release. Hmm."))
    # Compute the new semver compliant version number.
    version = compute_version(release_type)
    # Ask user to verify version and changesets.
    puts(c.blue("Changes to release:"))
    puts(c.cyan(changes))
    if not confirm("Are the changes and version correct?"):
        abort(c.red("Aborting release"))

    return version, changes


def release(branch, release_type):
    """Release a new version.

    :branch,release_type

    branch to be released
    release_type: see fab -d compute_version

    Preflight, runs tests, bumps version number, tags repo and uploads to pypi.
    """
    _invirt()
    with settings(hide('stderr', 'stdout', 'running')):
        # Preflight checks.
        version, changes = _sync_and_preflight_check(branch, release_type)
        puts(c.blue("Testing..."))
        # Lets check out this branch and test it.
        local("git checkout %s" % branch,  capture=True)
        test()
        puts(c.green("Tests passed!"))
        puts(c.blue("Build, package and publish..."))
        # Commit to the version file.
        local('echo "%s" > VERSION' % version)
        # Build
        local("python setup.py register sdist bdist_egg upload")
        puts(c.green("Uploaded to PyPI!"))
        # Commit the version change and tag the release.
        puts(c.blue("Commit, tag, merge, prune and push."))
        local('git commit -m"Bumped version to v%s" -a' % version)
        local('git tag -a "v%s" -m "Release version %s"' % (version, version))
        # Merge the branch into master and push them both to origin
        # Conflicts should never occur, due to preflight checks.
        local('git checkout master', capture=True)
        local('git merge %s' % branch, capture=True)
        local('git branch -d %s' % branch)
        local('git push origin :%s' % branch)  # This deletes remote branch.
        local('git push --tags origin master')
        puts(c.magenta("Released branch %s as v%s!" % (branch, version)))
        post_release_install_verification()
