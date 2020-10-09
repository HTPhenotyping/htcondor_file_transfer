#!/usr/bin/env python3
"""
Usage:
  snapshot.py [-v] make <dir>
  snapshot.py [-v] compare <s1> <s2>

Take and compare snapshots of file hierarchies. A snapshot is a JSON object
recording the path to the root of the file hierarchy and metadata about each
file under that root. Results are shown on standard out.

Options:
  -v          Log debugging messages to standard error
  -h, --help  Show this message and exit
"""

import contextlib
import hashlib
import json
import logging
import os
import stat
from pathlib import Path
from typing import Dict, Iterator

import docopt

LOGGING_NAME = "ba_snapshot"

BUFFER_SIZE = 1024 * 1024

#
# Type definitions.
#

FSPath = str
TypedDict = object  # TODO: Remove this definition with Python >= 3.8


class FileMetadata(TypedDict):
    size: int
    sha512: str


FileManifest = Dict[FSPath, FileMetadata]


class Snapshot(TypedDict):
    root: FSPath
    manifest: FileManifest


############################################################################


@contextlib.contextmanager
def chdir(path: FSPath) -> Iterator[None]:
    """
    Implements a context manager for changing the current working directory.
    """
    oldcwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(oldcwd)


def sha512(path: FSPath, mode: int) -> str:
    """
    Computes a SHA-512 hash for the file at the given path.
    """
    path = os.fspath(path)
    hash = hashlib.sha512()

    if stat.S_ISREG(mode):
        with open(path, "rb") as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break
                hash.update(data)
    elif stat.S_ISLNK(mode):
        hash.update(bytes(os.readlink(path), "utf-8"))
    else:
        raise RuntimeError(f"Not a regular file or symlink: {path}")
    return hash.hexdigest()


def make_manifest(root: FSPath) -> FileManifest:
    """
    Computes the file manifest for the file hierarchy rooted at the given path.
    """
    manifest: FileManifest = {}
    log = logging.getLogger(LOGGING_NAME)

    for (dirpath, dirnames, filenames) in os.walk(root):
        dirnames[:] = sorted(dirnames)

        for filename in sorted(filenames):
            path = os.fspath(Path(dirpath) / filename)
            stat = os.lstat(path)

            log.info(f"PATH {path}")

            manifest[path] = {
                "size": stat.st_size,
                "sha512": sha512(path, stat.st_mode),
            }
    return manifest


def compare_snapshots(s1: Snapshot, s2: Snapshot) -> None:
    """
    Prints any differences found between the two snapshots.
    """
    r1 = s1["root"]
    r2 = s2["root"]

    if r1 == r2:
        r1 += "@1"
        r2 += "@2"

    m1 = s1["manifest"]
    m2 = s2["manifest"]

    paths1 = set(m1)
    paths2 = set(m2)

    for path in paths1 - paths2:
        print(f"In '{r1}' but not '{r2}': {path}")
    for path in paths2 - paths1:
        print(f"In '{r2}' but not '{r1}': {path}")

    for path in paths1 & paths2:
        if m1[path] != m2[path]:
            print(f"Files differ: {path}")


def main() -> None:
    """
    Main entry point, when called as a command-line utility.
    """
    args = docopt.docopt(__doc__)

    if args["-v"]:
        logging.basicConfig(
            level=logging.DEBUG, format="[%(asctime)s] %(levelname)s %(message)s",
        )

    if args["make"]:
        root = args["<dir>"]

        with chdir(root):
            manifest = make_manifest(".")

        snapshot: Snapshot = {
            "root": os.fspath(Path(root).resolve()),
            "manifest": manifest,
        }
        print(json.dumps(snapshot, indent=2, sort_keys=True))

    if args["compare"]:
        with open(args["<s1>"]) as file:
            s1 = json.load(file)
        with open(args["<s2>"]) as file:
            s2 = json.load(file)
        compare_snapshots(s1, s2)


if __name__ == "__main__":
    main()
