from pathlib import Path

import pytest

import xfer


@pytest.mark.parametrize("name", [Path("foobar"), Path("i have spaces")])
@pytest.mark.parametrize("timestamp", [1234, 1234.5678])
def test_round_trip_manifest_entries(tmp_path, name, timestamp):
    entries = [
        xfer.TransferRequest(name=name, size=123),
        xfer.VerifyRequest(name=name, size=123),
        xfer.TransferComplete(name=name, size=123, digest="abcd", timestamp=timestamp),
        xfer.SyncRequest(
            direction=xfer.TransferDirection.PULL,
            timestamp=1234,
            bytes_to_verify=10,
            files_to_verify=10,
            remote_prefix=Path("/a/path"),
            bytes_to_transfer=10,
            files_to_transfer=10,
            files_at_source=10,
        ),
        xfer.SyncDone(timestamp=timestamp),
        xfer.File(name=name, size=123),
        xfer.Metadata(name=name, size=123, digest="abcd"),
    ]

    tmp_file = tmp_path / "tmp"

    with tmp_file.open(mode="w") as f:
        for entry in entries:
            entry.write_entry_to(f)

    read_entries = list(entry for entry, _ in xfer.read_manifest(tmp_file))

    assert entries == read_entries


def test_manifest_comments_and_blank_lines_are_ignored(tmp_path):
    text = """\
    FILE {"name": "foobar", "size": 123}
    # I am a comment

    FILE {"name": "foobar", "size": 123}

    """

    tmp_file = tmp_path / "tmp"
    tmp_file.write_text(text)

    assert len(list(xfer.read_manifest(tmp_file))) == 2
