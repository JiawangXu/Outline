import os
import tempfile
import shutil
import pytest
from utils import create_folder

@pytest.fixture
def temp_dir():
    """Fixture for temporary directory, provides a fresh directory instance for each test function"""
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)

def test_create_folder_basic(temp_dir):
    test_path = os.path.join(temp_dir, "new_dir")
    create_folder(test_path)
    assert os.path.exists(test_path)
