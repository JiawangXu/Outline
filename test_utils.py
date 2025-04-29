import os
import tempfile
import shutil
import pytest
from utils import create_folder,get_files

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

def test_get_files(temp_dir):
    open(os.path.join(temp_dir, "file1.txt"), 'w').close()
    open(os.path.join(temp_dir, "file2.jpg"), 'w').close()
    open(os.path.join(temp_dir, "file3.jpg"), 'w').close()

    jpg_files = get_files(temp_dir, ext="jpg")
    assert len(jpg_files) == 2
    assert jpg_files[0].endswith('.jpg')
