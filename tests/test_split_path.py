from template_fragments import split_path

import pytest


@pytest.mark.parametrize(
    "path_with_fragment, expected_path, expected_fragment",
    [
        ("index.html", "index.html", ""),
        ("index.html#", "index.html", ""),
        ("index.html#child", "index.html", "child"),
        ("index.html#path#fragment", "index.html#path", "fragment"),
        ("/root/index.html", "/root/index.html", ""),
        ("/root/index.html#hello-world", "/root/index.html", "hello-world"),
    ],
)
def test_examples(path_with_fragment, expected_path, expected_fragment):
    actual_path, actual_fragment = split_path(path_with_fragment)

    assert actual_path == expected_path
    assert actual_fragment == expected_fragment
