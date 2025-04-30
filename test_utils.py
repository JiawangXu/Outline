import os
import tempfile
import shutil
import pytest
import numpy as np
from utils import create_folder,get_files,rearrange_numbers,get_mask_range

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


@pytest.mark.parametrize("input_str,expected", [
    ("AB12CD34", "1234"),
    ("(0028,1050)", "00281050"),
    ("NoNumbersHere", ""),
])
def test_rearrange_numbers(input_str, expected):
    assert rearrange_numbers(input_str) == expected

def test_get_mask_range():
    mask = np.zeros((10, 100, 100), dtype=np.uint8)
    mask[3:7, 20:80, 20:80] = 1

    first, last = get_mask_range(mask)
    assert first == 3
    assert last == 7


def test_empty_mask_range():
    empty_mask = np.zeros((5, 50, 50), dtype=np.uint8)
    first, last = get_mask_range(empty_mask)
    assert first == 0
    assert last == 5
