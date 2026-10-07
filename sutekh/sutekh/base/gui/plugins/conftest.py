# Custom hook to ensure we add the plugin files to the list
# of possible test sources. This allows including the
# plugin tests in the same file as the plugin.
# Tests are expected to be unittest test cases, like
# the non-plugin tests.
#
# This is mostly as an example for consumers to follow,
# but does allow us to include some simple non-database
# checks in the base plugins
import pytest

# This just adds all the plugin files in this directory
# to the test list - we rely on unittest discovery to then
# do the right thing
@pytest.hookimpl
def pytest_collect_file(file_path, path, parent):
    if file_path.suffix == '.py' and \
            file_path.name not in ('__init__.py', 'conftest.py'):
        return pytest.Module.from_parent(parent, path=file_path)
    return None
