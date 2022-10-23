import pytest

from jinja2 import DictLoader, Environment

from template_fragments import filter_template, split_template
from template_fragments.jinja import FragmentLoader

source = """\
<body>
<ul>
{% fragment listing %}
    {% for item in listing %}
    <li>{{ item }}</li>
    {% endfor %}
{% endfragment %}
</ul>
{% fragment content %}
<div>
    {% for item in content %}
    {% fragment content-item %}
    <div>{{ item }}</div>
    {% endfragment %}
    {% endfor %}
</div>
{% endfragment %}
</body>
"""

expected_complete = """\
<body>
<ul>
    {% for item in listing %}
    <li>{{ item }}</li>
    {% endfor %}
</ul>
<div>
    {% for item in content %}
    <div>{{ item }}</div>
    {% endfor %}
</div>
</body>
"""

expected_listing = """\
    {% for item in listing %}
    <li>{{ item }}</li>
    {% endfor %}
"""

expected_content = """\
<div>
    {% for item in content %}
    <div>{{ item }}</div>
    {% endfor %}
</div>
"""

expected_content_item = """\
    <div>{{ item }}</div>
"""

expected_fragments = [
    ("", expected_complete),
    ("listing", expected_listing),
    ("content", expected_content),
    ("content-item", expected_content_item),
]


@pytest.mark.parametrize("fragment, expected", expected_fragments)
def test_filter_template(fragment, expected):
    actual = filter_template(source, fragment)
    expected = expected

    assert actual == expected


def test_split_template():
    actual = split_template(source)
    expected = dict(expected_fragments)

    assert actual == expected


@pytest.mark.parametrize("fragment, expected_source", expected_fragments)
def test_jinja_fragment_loader(fragment, expected_source):
    env = Environment()
    base_loader = DictLoader({"index.html": source})
    loader = FragmentLoader(base_loader)

    actual_source, _, _ = loader.get_source(env, f"index.html#{fragment}")

    assert actual_source == expected_source
