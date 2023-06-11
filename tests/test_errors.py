import functools as ft

import pytest

from template_fragments import TemplateFragmentError, filter_template, split_templates

funcs = [
    split_templates,
    ft.partial(filter_template, fragment=""),
    ft.partial(filter_template, fragment="dummy"),
]


@pytest.mark.parametrize("func", funcs)
def test_reentrant_fragment(func):
    source = """
        {% fragment dummy %}
        {% fragment dummy %}
        {% endfragment %}
        {% endfragment %}
    """
    with pytest.raises(TemplateFragmentError):
        func(source)


@pytest.mark.parametrize("func", funcs)
def test_missing_names_for_start(func):
    source = """
        {% fragment %}
        {% endfragment %}
    """
    with pytest.raises(TemplateFragmentError):
        func(source)


@pytest.mark.parametrize("func", funcs)
def test_names_for_end(func):
    source = """
        {% fragment dummy %}
        {% endfragment dummy %}
    """
    with pytest.raises(TemplateFragmentError):
        func(source)


@pytest.mark.parametrize("func", funcs)
def test_missing_endfragment(func):
    source = """
        {% fragment example %}
    """
    with pytest.raises(TemplateFragmentError):
        func(source)


@pytest.mark.parametrize("func", funcs)
def test_to_many_endfragment(func):
    source = """
        {% fragment example %}
        {% endfragment %}
        {% endfragment %}
    """
    with pytest.raises(TemplateFragmentError):
        func(source)


@pytest.mark.parametrize("func", funcs)
def test_leading_content(func):
    source = """
        invalid {% fragment example %}
        {% endfragment %}
    """
    with pytest.raises(TemplateFragmentError):
        func(source)


@pytest.mark.parametrize("func", funcs)
def test_trailing_content(func):
    source = """
        {% fragment example %} invalid
        {% endfragment %}
    """
    with pytest.raises(TemplateFragmentError):
        func(source)
