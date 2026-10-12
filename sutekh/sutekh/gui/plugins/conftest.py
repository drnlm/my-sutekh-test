# Custom hook to ensure we add the plugin files to the list
# of possible test sources. This allows including the
# plugin tests in the same file as the plugin.
# Tests are expected to be unittest test cases, like
# the non-plugin tests.
import pytest

# Avoid gtk issues when running subsets of the tests
import gi
gi.require_version("Gtk", "3.0")

# We need to have the test fixtures imported here as well
# so they will be used in the plugin tests.
from sutekh.tests.conftest import db_setup, clean_db

# This just adds all the plugin files in this directory
# to the test list - we rely on unittest discovery to then
# do the right thing
@pytest.hookimpl
def pytest_collect_file(file_path, path, parent):
    if file_path.suffix == '.py' and \
            file_path.name not in ('__init__.py', 'conftest.py'):
        return pytest.Module.from_parent(parent, path=file_path)
    return None
