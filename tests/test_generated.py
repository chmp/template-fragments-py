import pytest

from template_fragments import split_templates, filter_template


def concat(*p: str) -> str:
    return "".join(p)


def test_reentrant_fragment():
    template = concat(
        "{% fragment dummy %}\n",
        "{% fragment dummy %}\n",
        "{% endfragment %}\n",
        "{% endfragment %}\n",
    )
    with pytest.raises(Exception):
        filter_template(template, "")
    with pytest.raises(Exception):
        filter_template(template, "dummy")
    with pytest.raises(Exception):
        split_templates(template)


def test_missing_name():
    template = concat(
        "{% fragment %}\n",
        "{% endfragment %}\n",
    )
    with pytest.raises(Exception):
        filter_template(template, "")
    with pytest.raises(Exception):
        filter_template(template, "dummy")
    with pytest.raises(Exception):
        split_templates(template)


def test_named_end():
    template = concat(
        "{% fragment dummy %}\n",
        "{% endfragment dummy %}\n",
    )
    with pytest.raises(Exception):
        filter_template(template, "")
    with pytest.raises(Exception):
        filter_template(template, "dummy")
    with pytest.raises(Exception):
        split_templates(template)


def test_missing_end():
    template = concat(
        "{% fragment example %}\n",
    )
    with pytest.raises(Exception):
        filter_template(template, "")
    with pytest.raises(Exception):
        filter_template(template, "dummy")
    with pytest.raises(Exception):
        split_templates(template)


def test_repeated_ends():
    template = concat(
        "{% fragment example %}\n",
        "{% endfragment %}\n",
        "{% endfragment %}\n",
    )
    with pytest.raises(Exception):
        filter_template(template, "")
    with pytest.raises(Exception):
        filter_template(template, "dummy")
    with pytest.raises(Exception):
        split_templates(template)


def test_trailing_content():
    template = concat(
        "{% fragment example %} invalid\n",
        "{% endfragment %}\n",
    )
    with pytest.raises(Exception):
        filter_template(template, "")
    with pytest.raises(Exception):
        filter_template(template, "dummy")
    with pytest.raises(Exception):
        split_templates(template)


def test_example_1():
    template = concat(
        "<body>\n",
        "<ul>\n",
        "{% fragment listing %}\n",
        "    {% for item in listing %}\n",
        "    <li>{{ item }}</li>\n",
        "    {% endfor %}\n",
        "{% endfragment %}\n",
        "</ul>\n",
        "{% fragment content %}\n",
        "<div>\n",
        "    {% for item in content %}\n",
        "    {% fragment content-item %}\n",
        "    <div>{{ item }}</div>\n",
        "    {% endfragment %}\n",
        "    {% endfor %}\n",
        "</div>\n",
        "{% endfragment %}\n",
        "</body>\n",
    )
    expected = {
        "": concat(
            "<body>\n",
            "<ul>\n",
            "    {% for item in listing %}\n",
            "    <li>{{ item }}</li>\n",
            "    {% endfor %}\n",
            "</ul>\n",
            "<div>\n",
            "    {% for item in content %}\n",
            "    <div>{{ item }}</div>\n",
            "    {% endfor %}\n",
            "</div>\n",
            "</body>\n",
        ),
        "listing": concat(
            "    {% for item in listing %}\n",
            "    <li>{{ item }}</li>\n",
            "    {% endfor %}\n",
        ),
        "content": concat(
            "<div>\n",
            "    {% for item in content %}\n",
            "    <div>{{ item }}</div>\n",
            "    {% endfor %}\n",
            "</div>\n",
        ),
        "content-item": concat(
            "    <div>{{ item }}</div>\n",
        ),
    }
    assert filter_template(template, "") == expected[""]
    assert filter_template(template, "listing") == expected["listing"]
    assert filter_template(template, "content") == expected["content"]
    assert filter_template(template, "content-item") == expected["content-item"]
    assert split_templates(template) == expected


def test_example_2():
    template = concat(
        "<body>\n",
        "    {% for item in items %}\n",
        "    {% fragment item %}\n",
        "    <div>\n",
        "        {{ item }}\n",
        "    </div>\n",
        "    {% endfragment %}\n",
        "    {% endfor %}\n",
        "<body>\n",
    )
    expected = {
        "": concat(
            "<body>\n",
            "    {% for item in items %}\n",
            "    <div>\n",
            "        {{ item }}\n",
            "    </div>\n",
            "    {% endfor %}\n",
            "<body>\n",
        ),
        "item": concat(
            "    <div>\n",
            "        {{ item }}\n",
            "    </div>\n",
        ),
    }
    assert filter_template(template, "") == expected[""]
    assert filter_template(template, "item") == expected["item"]
    assert split_templates(template) == expected


@pytest.mark.xfail
def test_block_fragments():
    template = concat(
        "<body>\n",
        "  {% for item in items %}\n",
        "  {% fragment-block item %}\n",
        "    <div>\n",
        "      {{ item }}\n",
        "    </div>\n",
        "  {% endfragment-block %}\n",
        "  {% endfor %}\n",
        "<body>\n",
    )
    expected = {
        "": concat(
            "<body>\n",
            "  {% for item in items %}\n",
            "  {% block item %}\n",
            "    <div>\n",
            "      {{ item }}\n",
            "    </div>\n",
            "  {% endblock %}\n",
            "  {% endfor %}\n",
            "<body>\n",
        ),
        "item": concat(
            "  {% block item %}\n",
            "    <div>\n",
            "      {{ item }}\n",
            "    </div>\n",
            "  {% endblock %}\n",
        ),
    }
    assert filter_template(template, "") == expected[""]
    assert filter_template(template, "item") == expected["item"]
    assert split_templates(template) == expected


@pytest.mark.xfail
def test_nested_block_fragments():
    template = concat(
        "<body>\n",
        "  {% fragment-block outer %}\n",
        "  {% for item in items %}\n",
        "  {% fragment-block item %}\n",
        "    <div>\n",
        "      {{ item }}\n",
        "    </div>\n",
        "  {% endfragment-block %}\n",
        "  {% endfor %}\n",
        "  {% endfragment-block %}\n",
        "<body>\n",
    )
    expected = {
        "": concat(
            "<body>\n",
            "  {% block outer %}\n",
            "  {% for item in items %}\n",
            "  {% block item %}\n",
            "    <div>\n",
            "      {{ item }}\n",
            "    </div>\n",
            "  {% endblock %}\n",
            "  {% endfor %}\n",
            "  {% endblock %}\n",
            "<body>\n",
        ),
        "item": concat(
            "  {% block item %}\n",
            "    <div>\n",
            "      {{ item }}\n",
            "    </div>\n",
            "  {% endblock %}\n",
        ),
        "outer": concat(
            "  {% block outer %}\n",
            "  {% for item in items %}\n",
            "  {% block item %}\n",
            "    <div>\n",
            "      {{ item }}\n",
            "    </div>\n",
            "  {% endblock %}\n",
            "  {% endfor %}\n",
            "  {% endblock %}\n",
        ),
    }
    assert filter_template(template, "") == expected[""]
    assert filter_template(template, "item") == expected["item"]
    assert filter_template(template, "outer") == expected["outer"]
    assert split_templates(template) == expected


def test_repeated_fragment():
    template = concat(
        "{% fragment foo bar %}\n",
        "    <common>\n",
        "{% endfragment %}\n",
        "{% fragment foo %}\n",
        "    <foo>\n",
        "{% endfragment %}\n",
        "{% fragment bar %}\n",
        "    <bar>\n",
        "{% endfragment %}\n",
    )
    expected = {
        "": concat(
            "    <common>\n",
            "    <foo>\n",
            "    <bar>\n",
        ),
        "foo": concat(
            "    <common>\n",
            "    <foo>\n",
        ),
        "bar": concat(
            "    <common>\n",
            "    <bar>\n",
        ),
    }
    assert filter_template(template, "") == expected[""]
    assert filter_template(template, "foo") == expected["foo"]
    assert filter_template(template, "bar") == expected["bar"]
    assert split_templates(template) == expected
