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

[flask]: https://flask.palletsprojects.com/en/2.2.x/
[jinja2]: https://jinja.palletsprojects.com/en/3.0.x/
