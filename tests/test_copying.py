import string

import pytest

import xfer


@pytest.fixture
def src(tmp_path):
    return tmp_path / "src"


@pytest.fixture
def dest(tmp_path):
    return tmp_path / "dest"


@pytest.mark.parametrize("size", [10, 10000, 10000000])
def test_hashes_equal_after_copy(src, dest, size):
    src.write_text(string.ascii_letters * size)

    src_hasher, src_bytes = xfer.hash_file(src)

    dest_hasher, dest_bytes = xfer.copy_with_hash(src, dest)

    assert src_bytes == dest_bytes
    assert src_hasher.hexdigest() == dest_hasher.hexdigest()


def test_destination_doesnt_exist_if_copy_fails(src, dest):
    try:
        # this will fail since we didn't actually make a source file
        xfer.copy_with_hash(src, dest)
    except FileNotFoundError:
        pass

    assert not dest.exists()
