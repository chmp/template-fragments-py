# Template fragments for jinja-like engines

[API reference](#api-reference)
| [License](#license)

Usage:

```python
from template_fragments import filter_template

template_source = """
<html>
    <head>
        <title>Example</title>
    </head>
    <body>
        <div>
        {% fragment content %}
            <!-- content here -->
        {% endfragment %}
        </div>
    </body>
</html>
"""

content_full = filter_template(template_source, "")
content_item = filter_template(template_source, "item")
```

Usage with [Flask][flask] and [Jinja2][jinja2]:

```python
from template_fragments.jinja import FragmentLoader

app.jinja_loader = FragmentLoader(app.jinja_loader)


@app.route("/")
def get_index():
    return render_template("index.html", ...)


@app.route("/item/<item>")
def get_item(item):
    return render_template("index.html#item", ...)
```

## API reference

<!-- minidoc "module": "template_fragments", "header": false -->

### `template_fragments.split_templates`

[template_fragments.split_templates]: #template_fragmentssplit_templates

`template_fragments.split_templates(src: str) -> Dict[str, str]`

Return all fragments contained in the template

The key `""` gives the source template with any fragment directives removed.

### `template_fragments.filter_template`

[template_fragments.filter_template]: #template_fragmentsfilter_template

`template_fragments.filter_template(src: str, fragment: str = '') -> str`

Return the parts of the template for the given fragment

Parameters:

- `src`: the template source
- `fragment`: the fragment to return. If `fragment = ""`, removes any
  fragment directives

### `template_fragments.split_path`

[template_fragments.split_path]: #template_fragmentssplit_path

`template_fragments.split_path(path: str) -> Tuple[str, str]`

Split the fragment from the path

### `template_fragments.TemplateFragmentError`

[template_fragments.TemplateFragmentError]: #template_fragmentstemplatefragmenterror

`template_fragments.TemplateFragmentError`

Common base class for all non-exit exceptions.

<!-- minidoc -->

### `template_fragments.jinja`

<!-- minidoc "module": "template_fragments.jinja", "header": false -->
Jinja specific helpers

#### `template_fragments.jinja.FragmentLoader`

[template_fragments.jinja.FragmentLoader]: #template_fragmentsjinjafragmentloader

`template_fragments.jinja.FragmentLoader(base_loader: jinja2.loaders.BaseLoader)`

A loader that filters fragments

<!-- minidoc -->


## License

```
The MIT License (MIT)
Copyright (c) 2022 - 2023 Christopher Prohm

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
```

[flask]: https://flask.palletsprojects.com/
[jinja2]: https://jinja.palletsprojects.com/
