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
from pathlib import Path
from typing import Dict, Union

import docopt

LOGGING_NAME = "snapshot"

BUFFER_SIZE = 2 ** 20  # 1 MiB

#
# Type definitions.
#

FSPath = str
AnyPath = Union[Path, FSPath]
TypedDict = object  # TODO: Import from 'typing' with Python >= 3.8


class FileMetadata(TypedDict):
    size: int
    sha1_digest: str


FileManifest = Dict[FSPath, FileMetadata]


class Snapshot(TypedDict):
    version: str
    root: FSPath
    manifest: FileManifest


############################################################################


def sha1(path: AnyPath, mode: int) -> str:
    """
    Computes the SHA-1 hash for the file at the given path.
    """
    hash = hashlib.sha1()

    if stat.S_ISREG(mode):
        with open(path, "rb") as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break
                hash.update(data)
    else:
        message = f"Not a regular file: {path}"

        log = logging.getLogger(LOGGING_NAME)
        log.error(message)

        raise RuntimeError(message)

    return hash.hexdigest()


def make_manifest(root: AnyPath) -> FileManifest:
    """
    Computes the file manifest for the given directory.
    """
    manifest: FileManifest = {}
    log = logging.getLogger(LOGGING_NAME)

    for (dirpath, dirnames, filenames) in os.walk(root):
        dirnames[:] = sorted(dirnames)

        for filename in sorted(filenames):
            path = Path(dirpath) / filename

            log.info(f"PATH {path}")

            st_info = path.lstat()
            rel_path = os.fspath(path.relative_to(root))

            manifest[rel_path] = {
                "size": st_info.st_size,
                "sha1_digest": sha1(path, st_info.st_mode),
            }
    return manifest


def compare_snapshots(s1: Snapshot, s2: Snapshot) -> None:
    """
    Prints any differences found between the two given snapshots.
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

    if args["--verbose"]:
        logging.basicConfig(
            level=logging.DEBUG, format="[%(asctime)s] %(levelname)s %(name)s %(message)s",
        )

    if args["make"]:
        dir = args["<dir>"]

        root = os.fspath(Path(dir).resolve())

        snapshot: Snapshot = {
            "version": "2",
            "root": root,
            "manifest": make_manifest(root),
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
