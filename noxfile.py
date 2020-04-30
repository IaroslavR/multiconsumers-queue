"""Nox sessions.

References:
    https://github.com/cjolowicz/hypermodern-python/blob/master/noxfile.py
"""

import tempfile
from typing import Any

import nox
from nox.sessions import Session


package = "multiconsumers_queue"
nox.options.sessions = ["tests"]
locations = "src", "tests", "noxfile.py", "docs/conf.py"


def install_with_constraints(session: Session, *args: str, **kwargs: Any) -> None:
    """Install packages constrained by Poetry's lock file.

    This function is a wrapper for nox.sessions.Session.install. It
    invokes pip to install packages inside of the session's virtualenv.
    Additionally, pip is passed a constraints file generated from
    Poetry's lock file, to ensure that the packages are pinned to the
    versions specified in poetry.lock. This allows you to manage the
    packages as Poetry development dependencies.

    Args:
        session: The Session object.
        *args: Command-line arguments for pip.
        **kwargs: Additional keyword arguments for Session.install.
    """
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--extras",
            "dev",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


@nox.session(python=["3.7"])
def tests(session: Session) -> None:
    """Run the test suite.

    Args:
        session: The Session object.
    """
    args = session.posargs or []
    session.run("which", "python")
    session.run("poetry", "env", "list", external=True)
    # session.run("poetry", "env", "use", "python", "-vvv", external=True)
    session.run("poetry", "env", "list", external=True)
    session.run("poetry", "install", "--no-dev", "-vvv", external=True)
    install_with_constraints(session, "coverage[toml]", "pytest")
    session.run("pytest", *args)
