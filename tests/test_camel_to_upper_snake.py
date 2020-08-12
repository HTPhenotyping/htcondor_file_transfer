import pytest

from xfer import camel_to_upper_snake


@pytest.mark.parametrize(
    "input, output",
    [
        ("CamelCase", "CAMEL_CASE"),
        ("AlTeRnAtInG", "AL_TE_RN_AT_IN_G"),
        ("foobar", "FOOBAR"),
        ("FOOBAR", "FOOBAR"),
        ("fooBar", "FOO_BAR"),
        ("DAGMan", "DAG_MAN"),
        ("twoGroups", "TWO_GROUPS"),
    ],
)
def test_camel_to_upper_snake(input, output):
    assert camel_to_upper_snake(input) == output
