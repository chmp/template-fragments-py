import pytest

from flask import Flask, render_template

from template_fragments.jinja import FragmentLoader

app = Flask(__name__)
app.jinja_loader = FragmentLoader(app.jinja_loader)

listing = ["hello", "world"]
content = ["foo", "bar", "baz"]


@app.route("/")
def get_index():
    return render_template("index.html", listing=listing, content=content)


@app.route("/listing")
def get_listing():
    return render_template("index.html#listing", listing=listing)


@app.route("/content")
def get_content():
    return render_template("index.html#content", content=content)


@app.route("/item/<item>")
def get_item(item):
    return render_template("index.html#content-item", item=item)


expected_index = """\
<body>
<ul>
    <li>hello</li>
    <li>world</li>
</ul>
<div>
    <div>foo</div>
    <div>bar</div>
    <div>baz</div>
</div>
</body>\
"""

expected_listing = """
    <li>hello</li>
    <li>world</li>\
"""

expected_content = """\
<div>
    <div>foo</div>
    <div>bar</div>
    <div>baz</div>
</div>\
"""

expected_item = """\
    <div>foo</div>\
"""

examples = [
    ("/", expected_index),
    ("/listing", expected_listing),
    ("/content", expected_content),
    ("/item/foo", expected_item),
]


@pytest.mark.parametrize("route, expected", examples)
def test_index(route, expected):
    response = app.test_client().get(route)
    actual = response.text

    assert actual == expected
