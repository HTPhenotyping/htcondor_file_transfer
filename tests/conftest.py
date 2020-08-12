import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
REPOSITORY_DIR = TESTS_DIR.parent

sys.path.append(REPOSITORY_DIR)
