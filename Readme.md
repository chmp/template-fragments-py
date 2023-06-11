# Template fragments for jinja-like engines

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

Usage with [Flask]:

```python
from template_fragments.jinja import FragmentLoader

app.jinja_loader = FragmentLoader(app.jinja_loader)
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

###  `template_fragments.jinja``

<!-- minidoc "module": "template_fragments.jinja", "header": false -->
Jinja specific helpers

#### `template_fragments.jinja.FragmentLoader`

[template_fragments.jinja.FragmentLoader]: #template_fragmentsjinjafragmentloader

`template_fragments.jinja.FragmentLoader(base_loader: jinja2.loaders.BaseLoader)`

A loader that filters fragments

<!-- minidoc -->


[flask]: https://flask.palletsprojects.com/en/2.2.x/
[jinja2]: https://jinja.palletsprojects.com/en/3.0.x/
