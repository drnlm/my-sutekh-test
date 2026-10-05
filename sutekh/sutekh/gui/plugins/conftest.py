# Custom hook to ensure we add the plugin files to the list
# of possible test sources.
import pytest

# We need to have the test fixtures here as well
from sutekh.tests.conftest import db_setup, clean_db

# This just adds all the pytest files in this directory
# to the test list - we rely on unittest discovery to then
# do the right thing
@pytest.hookimpl
def pytest_collect_file(file_path, path, parent):
    if file_path.suffix == '.py':
        return pytest.Module.from_parent(parent, path=file_path)
    return None
