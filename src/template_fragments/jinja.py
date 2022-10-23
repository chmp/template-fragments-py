"""Jinja specific helpers"""
from ._base import filter_template, split_path

import jinja2


class FragmentLoader(jinja2.BaseLoader):
    """A loader that filters fragments"""

    def __init__(self, base_loader: jinja2.BaseLoader):
        super().__init__()
        self.base_loader = base_loader

    def get_source(self, environment: jinja2.Environment, path: str):
        template, fragment = split_path(path)
        source, filename, uptodate = self.base_loader.get_source(environment, template)
        return filter_template(source, fragment), filename, uptodate
