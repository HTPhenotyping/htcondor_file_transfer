import string

import pytest

import xfer


@pytest.mark.parametrize("size", [10, 10000, 10000000])
def test_hashes_equal_after_copy(tmp_path, size):
    src = tmp_path / "src"
    dest = tmp_path / "dest"

    src.write_text(string.ascii_letters * size)

    src_hasher, src_bytes = xfer.hash_file(src)

    dest_hasher, dest_bytes = xfer.copy_with_hash(src, dest)

    assert src_bytes == dest_bytes
    assert src_hasher.hexdigest() == dest_hasher.hexdigest()
