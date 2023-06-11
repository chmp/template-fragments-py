import pytest

from jinja2 import DictLoader, Environment

from template_fragments import filter_template, split_templates
from template_fragments.jinja import FragmentLoader

source = """\
{% fragment foo bar %}
    <common>
{% endfragment %}
{% fragment foo %}
    <foo>
{% endfragment %}
{% fragment bar %}
    <bar>
{% endfragment %}
"""

expected_complete = """\
    <common>
    <foo>
    <bar>
"""

expected_foo = """\
    <common>
    <foo>
"""

expected_bar = """\
    <common>
    <bar>
"""

expected_fragments = [
    ("", expected_complete),
    ("foo", expected_foo),
    ("bar", expected_bar),
]


@pytest.mark.parametrize("fragment, expected", expected_fragments)
def test_filter_template(fragment, expected):
    actual = filter_template(source, fragment)
    expected = expected

    assert actual == expected


def test_split_templates():
    actual = split_templates(source)
    expected = dict(expected_fragments)

    assert actual == expected


@pytest.mark.parametrize("fragment, expected_source", expected_fragments)
def test_jinja_fragment_loader(fragment, expected_source):
    env = Environment()
    base_loader = DictLoader({"index.html": source})
    loader = FragmentLoader(base_loader)

    actual_source, _, _ = loader.get_source(env, f"index.html#{fragment}")

    assert actual_source == expected_source
