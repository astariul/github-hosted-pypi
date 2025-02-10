import subprocess
import os
from importlib.metadata import PackageNotFoundError, version
from contextlib import contextmanager


@contextmanager
def run_local_pypi_index():
    # WARNING : This requires the script to be run from the root of the repo
    p = subprocess.Popen(["python", "-m", "http.server"])
    try:
        yield
    finally:
        p.terminate()


def exists(pkg_name: str) -> bool:
    try:
        version(pkg_name)
    except PackageNotFoundError:
        return False
    else:
        return True


def pip_install(pkg_name: str, upgrade: bool = False, version: str = None):
    package_to_install = pkg_name if version is None else f"{pkg_name}=={version}"
    cmd = ["python", "-m", "pip", "install", package_to_install, "--upgrade" if upgrade else "", "--extra-index-url", "http://localhost:8000"]
    subprocess.run([c for c in cmd if c])


def pip_uninstall(pkg_name: str):
    subprocess.run(["python", "-m", "pip", "uninstall", pkg_name, "-y"])


def register(pkg_name: str, pkg_version: str, pkg_link: str):
    env = os.environ.copy()
    env["PKG_ACTION"] = "REGISTER"
    env["PKG_NAME"] = pkg_name
    env["PKG_VERSION"] = pkg_version
    env["PKG_AUTHOR"] = "Dummy author"
    env["PKG_SHORT_DESC"] = "Dummy Description"
    env["PKG_HOMEPAGE"] = pkg_link
    subprocess.run(["python", ".github/actions.py"], env=env)


def update(pkg_name: str, pkg_version: str):
    env = os.environ.copy()
    env["PKG_ACTION"] = "UPDATE"
    env["PKG_NAME"] = pkg_name
    env["PKG_VERSION"] = pkg_version
    subprocess.run(["python", ".github/actions.py"], env=env)


def delete(pkg_name: str):
    env = os.environ.copy()
    env["PKG_ACTION"] = "DELETE"
    env["PKG_NAME"] = pkg_name
    subprocess.run(["python", ".github/actions.py"], env=env)


def run_tests():
    # This test is checking that the Github actions for registering, updating,
    # and deleting are working and the PyPi index is updated accordingly.
    # What we do is :
    #  * Serve the HTML locally so we have a local PyPi index
    #  * Run the actions for registering, updating, and deleting packages in
    #    this local PyPi
    #  * In-between, run some basic checks to see if the installation is
    #    working properly
    with run_local_pypi_index():
        # First, make sure the package is not installed
        assert not exists("public-hello")

        # The package `public-hello` is already registered in our local PyPi
        # ACTION : Let's remove it from our local PyPi
        delete("public-hello")

        # Trying to install the package, only the version uploaded to PyPi (0.0.0)
        # will be detected and installed (the version in our local PyPi was
        # successfully deleted)
        pip_install("public-hello")
        assert exists("public-hello") and version("public-hello") == "0.0.0"

        # ACTION : Register the package, to make it available again
        register("public-hello", "0.1", "https://github.com/astariul/public-hello")

        # Now we can install it from the local PyPi
        pip_install("public-hello", upgrade=True)
        assert exists("public-hello") and version("public-hello") == "0.1"

        # ACTION : Update the package with a new version
        update("public-hello", "0.2")

        # We can update the package to the newest version
        pip_install("public-hello", upgrade=True)
        assert exists("public-hello") and version("public-hello") == "0.2"

        # We should still be able to install the old version
        pip_install("public-hello", version="0.1")
        assert exists("public-hello") and version("public-hello") == "0.1"

        # Uninstall the package (for consistency with the initial state)
        pip_uninstall("public-hello")
        assert not exists("public-hello")


if __name__ == "__main__":
    run_tests()
