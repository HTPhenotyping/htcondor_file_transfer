#!/usr/bin/env python3
"""
Usage:
  snapshot [-v] (make <dir> | compare <s1> <s2>)

A snapshot records the path to a directory and metadata for each file in
that directory. Snapshots are compared by checking whether their respective
directories contain the same files, each with the same metadata.

Options:
  -h, --help     Show this message and exit
  -v, --verbose  Log debugging messages to standard error
"""

import hashlib
import json
import logging
import os
import stat
import sys
from pathlib import Path
from typing import Dict, NamedTuple, Union

import docopt

BUFFER_SIZE = 2 ** 20  # 1 MiB

FSPath = str
AnyPath = Union[FSPath, os.PathLike]


class FileMetadata(NamedTuple):
    size: int
    digest: str


FileManifest = Dict[FSPath, FileMetadata]


class Snapshot(NamedTuple):
    version: str
    root: FSPath
    manifest: FileManifest


class SnapshotDecoder(json.JSONDecoder):
    def decode(self, s):
        obj = super().decode(s)

        obj[2] = {k: FileMetadata(*v) for k, v in obj[2].items()}

        return Snapshot(*obj)


def make_digest(path: AnyPath, mode: int) -> str:
    """
    Returns the SHA-1 hash for the file at the given path.
    """
    hasher = hashlib.sha1()

    if stat.S_ISREG(mode):
        with open(path, "rb") as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break
                hasher.update(data)
    else:
        raise RuntimeError(f"Not a regular file: {path}")

    return hasher.hexdigest()


def make_manifest(root: AnyPath) -> FileManifest:
    """
    Returns the file manifest for the given directory.
    """
    manifest = {}

    for (dirpath, dirnames, filenames) in os.walk(root):
        dirnames[:] = sorted(dirnames)

        for filename in sorted(filenames):
            path = Path(dirpath) / filename

            logging.info(f"PATH {path}")

            st_info = path.lstat()
            rel_path = os.fspath(path.relative_to(root))

            manifest[rel_path] = FileMetadata(
                size=st_info.st_size, digest=make_digest(path, st_info.st_mode),
            )

    return manifest


def compare_snapshots(s1: Snapshot, s2: Snapshot) -> None:
    """
    Prints any differences found between the two given snapshots.
    """
    r1 = s1.root
    r2 = s2.root

    if r1 == r2:
        r1 += "@1"
        r2 += "@2"

    m1 = s1.manifest
    m2 = s2.manifest

    paths1 = set(m1)
    paths2 = set(m2)

    for path in paths1 - paths2:
        print(f"Only in '{r1}': {path}")
    for path in paths2 - paths1:
        print(f"Only in '{r2}': {path}")

    for path in paths1 & paths2:
        if m1[path] != m2[path]:
            print(f"Files differ: {path}")


############################################################################
# Command-line interface.


def init_logging() -> None:
    logging.basicConfig(format="[%(asctime)s] %(levelname)s %(message)s")


def main() -> None:
    args = docopt.docopt(__doc__)

    if args["--verbose"]:
        logging.getLogger().setLevel(logging.DEBUG)

    if args["make"]:
        dir = args["<dir>"]

        root = os.fspath(Path(dir).resolve())

        snapshot = Snapshot(version="4", root=root, manifest=make_manifest(root))

        print(json.dumps(snapshot, indent=2, sort_keys=True))

    if args["compare"]:
        with open(args["<s1>"]) as file:
            s1 = json.load(file, cls=SnapshotDecoder)
        with open(args["<s2>"]) as file:
            s2 = json.load(file, cls=SnapshotDecoder)
        compare_snapshots(s1, s2)


if __name__ == "__main__":
    try:
        init_logging()
        main()
    except Exception as exn:
        logging.exception(f"Exception: {exn}")
        sys.exit(1)
