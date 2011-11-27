
import subprocess


def test_issue_12_build_installs():
    """."""
    returncode = subprocess.call("fab buildtest", shell=True)
    assert returncode == 0
