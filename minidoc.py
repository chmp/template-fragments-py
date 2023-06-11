"""Render module documentation to markdown

To use `minidoc`, follow these steps:

1. mark a section as documentation using HTML comments:

    ```markdown
    # My Documentation

    <!-- minidoc "module": "my_module" -->
    <!-- minidoc -->
    ```

2. Run minidoc as in `python -m chmp.minidoc MY_DOC.md`

`minidoc` will replace the content between the comments with the documentation
of the module. It preserves the comments itself. Therefore, it is safe to run
`minidoc` repeatedly on the same document.

Per default minidoc will render a header for the module. To disable this
behavior add `"header": false` to the initial comment, as in:

```markdown
<!-- minidoc "module": "my_module", "header": false -->
```

To execute doc tests using pytest, load the plugin. E.g., via a `conftest.py`
file:

```python
pytest_plugins = "chmp.minidoc"
```

And include a test function with the `minidoc` marker:

```python
: import pytest
:
@pytest.mark.minidoc("chmp.minidoc")
def test_docs(test):
    test()
```

The `test` function will execute a single code block in a test. To include setup
in tests, prefix lines with `: `. They are executed in tests, but not included
in the rendered documentation.
"""
#
# Copyright: Christopher Prohm, 2022
# Copied from https://github.com/chmp/libchmp/blob/main/src/chmp/minidoc.py
# License: MIT License
#
import collections
import dataclasses
import enum
import importlib
import inspect
import json
import pathlib
import re
import typing

from inspect import Parameter
from typing import Any, Iterable, List, Optional, Tuple, Union, cast

try:
    from typing import get_overloads

except ImportError:

    def get_overloads(f):
        return []


__all__ = ["update_docs", "update_docs_lines", "update_docs_str"]


def update_docs(path: Union[str, pathlib.Path]):
    """Update the documentation section inside a file

    The file is updated in-place.

    Usage:

    ```python ignore
    update_docs("Readme.md")
    ```
    """
    with open(path, "rt") as fobj:
        lines = list(fobj)

    lines = update_docs_lines(lines)

    with open(path, "wt") as fobj:
        for line in lines:
            fobj.write(f"{line.rstrip()}\n")


def update_docs_lines(lines: List[str]) -> List[str]:
    """Inject the documentation in a list of lines

    Usage:

    ```python
    : from chmp.minidoc import update_docs_lines
    :
    lines = ["# My documentation", "..."]
    lines = update_docs_lines(lines)

    assert isinstance(lines, list)
    ```
    """
    return list(_inject_docs(lines))


def update_docs_str(lines: str) -> str:
    """Inject the documentation in a string

    Usage:

    ```python
    : from chmp.minidoc import update_docs_str
    :
    doc = update_docs_str('''# My documentation
    ...
    ''')

    assert isinstance(doc, str)
    ```
    """
    return "\n".join(_inject_docs(lines.splitlines()))


_minidoc_start = re.compile(r"^<!--\s+minidoc\s+(?P<desc>.*)-->$")
_minidoc_end = re.compile(r"^<!--\s+minidoc\s+-->$")


def parse_line(line):
    if _minidoc_end.match(line) is not None:
        return MinidocEnd()

    m = _minidoc_start.match(line)
    if m is not None:
        desc = json.loads("{" + m.group("desc") + "}")
        if "module" in desc:
            object = desc.pop("module")
            object_type = ObjectType.MODULE

        elif "class" in desc:
            object = desc.pop("class")
            object_type = ObjectType.CLASS

        elif "function" in desc:
            object = desc.pop("function")
            object_type = ObjectType.FUNCTION

        else:
            raise ValueError()

        return MinidocStart(type=object_type, object=object, **desc)

    if line.startswith("###### "):
        return Header(depth=6)

    if line.startswith("##### "):
        return Header(depth=5)

    if line.startswith("#### "):
        return Header(depth=4)

    if line.startswith("### "):
        return Header(depth=3)

    if line.startswith("## "):
        return Header(depth=2)

    if line.startswith("# "):
        return Header(depth=1)

    if line.startswith("```"):
        return BlockCode()

    return None


@dataclasses.dataclass
class MinidocStart:
    type: "ObjectType"
    object: str
    header: bool = True
    rename: Optional[str] = None


class ObjectType(str, enum.Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"


@dataclasses.dataclass
class Header:
    depth: int


@dataclasses.dataclass
class BlockCode:
    pass


@dataclasses.dataclass
class MinidocEnd:
    pass


def _inject_docs(lines: Iterable[str]) -> Iterable[str]:
    current = None
    header_depth = 0
    in_code = False

    for idx, line in enumerate(lines):
        line = line.rstrip()
        ty = parse_line(line)

        if isinstance(ty, BlockCode):
            if current is None:
                yield line

            in_code = not in_code

        elif in_code:
            if current is None:
                yield line

        elif isinstance(ty, MinidocStart):
            if current is not None:
                raise ValueError(
                    "minidoc: detected documentation start while inside a"
                    f" documentation block (line: {idx + 1})"
                )

            else:
                yield line
                current = ty

        elif isinstance(ty, MinidocEnd):
            if current is not None:
                yield from render_docs(
                    current.type,
                    current.object,
                    header_depth,
                    include_header=current.header,
                    rename=current.rename,
                )
                yield line

                current = None

            else:
                raise ValueError(
                    "minidoc: detected documentation end without start (line"
                    f" {idx + 1})"
                )

        elif isinstance(ty, Header) and current is None:
            header_depth = ty.depth
            yield line

        elif current is None:
            yield line


def render_docs(
    type: ObjectType,
    object_name: str,
    header_depth: int,
    *,
    include_header: bool = True,
    rename: Optional[str] = None,
) -> Iterable[str]:
    if type is ObjectType.MODULE:
        module = importlib.import_module(object_name)
        render_name = object_name if rename is None else rename

        yield from render_module(
            render_name,
            module,
            header_depth=header_depth + 1,
            include_header=include_header,
        )

    elif type in {ObjectType.CLASS, ObjectType.FUNCTION}:
        assert rename is None
        module_name, _, item_name = object_name.rpartition(".")
        module = importlib.import_module(module_name)
        item = getattr(module, item_name)
        yield from render_item(
            module_name,
            module,
            item_name,
            item,
            header_depth=header_depth + 1,
            include_header=include_header,
        )

    else:
        raise RuntimeError(f"Unknown object type ({type})")


def render_module(
    module_name: str, module: Any, *, header_depth: int, include_header: bool = True
):
    if include_header:
        yield _render_header(f"`{module_name}`", header_depth)
        yield ""

    yield from process_doc(get_doc(module))
    yield ""

    for name, item in get_module_contents(module):
        yield from render_item(
            module_name,
            module,
            name,
            item,
            header_depth=header_depth + (1 if include_header else 0),
        )


def render_item(
    module_name: str,
    module: Any,
    item_name: str,
    item: Any,
    header_depth: int,
    *,
    include_header: bool = True,
) -> Iterable[str]:
    module_doc_name = "__" + str(item_name).replace(".", "_") + "_doc__"
    doc = getattr(module, module_doc_name, get_doc(item))
    overloads = get_overloads(item) if inspect.isfunction(item) else []

    if not overloads:
        overloads = [item]

    if include_header:
        header = f"`{module_name}.{item_name}`"

        yield _render_header(header, header_depth)
        yield ""
        yield f"[{module_name}.{item_name}]: #{header_to_link(header)}"
        yield ""

        for overload in overloads:
            yield f"`{module_name}.{item_name}{format_signature(overload)}`"
            yield ""

    yield from process_doc(doc)
    yield ""

    yield from render_members(module_name, module, item_name, item, header_depth)


def process_doc(doc: str) -> Iterable[str]:
    """Strip out any ignored lines from code examples"""
    in_code_block = False
    filter_lines = False

    for line in doc.splitlines():
        assert not filter_lines or (filter_lines and in_code_block)

        if line.startswith("```python") and "ignore" not in line:
            assert not in_code_block
            in_code_block = True
            filter_lines = True
            yield line

        elif line.startswith("```"):
            in_code_block = not in_code_block
            filter_lines = False
            yield line

        elif filter_lines and line.startswith("::"):
            yield line[1:]

        elif filter_lines and line.startswith(":"):
            continue

        else:
            yield line


def render_members(
    module_name: str, module: Any, item_name: str, item: Any, header_depth: int
) -> Iterable[str]:
    for member_name, member in getattr(item, "__dict__", {}).items():
        is_documented = (
            not member_name.startswith("_") and has_own_doc(member)
        ) or hasattr(module, f"__{item_name}_{member_name}_doc__")

        if not is_documented:
            continue

        yield from render_item(
            module_name,
            module,
            f"{item_name}.{member_name}",
            member,
            header_depth=header_depth + 1,
        )


def _render_header(header: Any, depth: int) -> str:
    return "#" * min(6, depth) + " " + str(header)


def get_module_contents(module: Any) -> Iterable[Tuple[str, Any]]:
    if hasattr(module, "__all__"):
        for name in module.__all__:
            yield name, getattr(module, name)

    else:
        for key, item in module.__dict__.items():
            if key.startswith("_"):
                continue

            if hasattr(item, "__module__") and item.__module__ != module.__name__:
                continue

            if callable(item) or hasattr(module, f"__{key}_doc__"):
                yield key, item


def header_to_link(header: str) -> str:
    for c in "`.()=*,<>[]:'\"":
        header = header.replace(c, "")

    header = header.replace(" ", "-")
    header = header.lower()

    return header


def splice_docs(readme: List[str], docs: List[str]) -> Iterable[str]:
    in_reference = False

    for line in readme:
        is_reference_start = line.startswith("## Reference")
        is_h2_header = line.startswith("## ")

        if not in_reference and not is_reference_start:
            yield line

        elif not in_reference and is_reference_start:
            yield line
            yield from docs

            in_reference = True

        elif in_reference and not is_h2_header:
            # ignore the line
            pass

        elif in_reference and is_h2_header:
            yield line
            in_reference = False


def has_own_doc(obj: Any) -> bool:
    doc = getattr(obj, "__doc__", None)
    class_doc = getattr(type(obj), "__doc__", None)

    # filters out objects like ints, which have a doc attribute due to their class
    return doc is not None and doc != class_doc


def get_doc(obj: Any) -> str:
    doc = inspect.getdoc(obj)
    return str(doc) if doc is not None else ""


def format_signature(func: Any) -> str:
    """Format the signature of a callable"""
    if inspect.isclass(func):
        func = func.__init__
        skip_first_arg = True

    else:
        skip_first_arg = False

    if not inspect.isfunction(func):
        return ""

    sig = inspect.signature(func)

    parts = []
    parameters: List[Union[Parameter, str]] = list(sig.parameters.values())

    if skip_first_arg:
        parameters = parameters[1:]

    # insert pseud-parameters to handle pos-only and kw-only parameters
    idx = 0
    while idx < len(parameters):
        current = cast(Parameter, parameters[idx])
        assert isinstance(current, Parameter)

        if idx == 0 and current.kind is Parameter.KEYWORD_ONLY:
            parameters.insert(0, "*")
            idx += 2
            continue

        prev = cast(Parameter, parameters[idx - 1])
        assert isinstance(prev, Parameter)

        if (
            idx != 0
            and current.kind is Parameter.KEYWORD_ONLY
            and prev.kind not in {Parameter.KEYWORD_ONLY, Parameter.VAR_POSITIONAL}
        ):
            parameters.insert(idx, "*")
            idx += 2

        elif (
            idx != 0
            and current.kind is not Parameter.POSITIONAL_ONLY
            and prev.kind is Parameter.POSITIONAL_ONLY
        ):
            parameters.insert(idx, "/")
            idx += 2

        else:
            idx += 1

    for param in parameters:
        if isinstance(param, str):
            parts.append(param)

        elif param.kind in {
            Parameter.POSITIONAL_ONLY,
            Parameter.POSITIONAL_OR_KEYWORD,
            Parameter.KEYWORD_ONLY,
        }:
            if param.default is Parameter.empty and param.annotation is Parameter.empty:
                parts.append(f"{param.name}")

            elif (
                param.default is not Parameter.empty
                and param.annotation is Parameter.empty
            ):
                parts.append(f"{param.name}={param.default!r}")

            elif (
                param.default is Parameter.empty
                and param.annotation is not Parameter.empty
            ):
                parts.append(f"{param.name}: {format_annotation(param.annotation)}")

            elif (
                param.default is not Parameter.empty
                and param.annotation is not Parameter.empty
            ):
                parts.append(
                    f"{param.name}: {format_annotation(param.annotation)} "
                    f"= {param.default!r}"
                )

        elif param.kind in {Parameter.VAR_POSITIONAL}:
            parts.append(f"*{param.name}")

        elif param.kind in {Parameter.VAR_KEYWORD}:
            parts.append(f"**{param.name}")

    args = "(" + ", ".join(parts) + ")"

    if sig.return_annotation is Parameter.empty:
        return args

    else:
        return f"{args} -> {format_annotation(sig.return_annotation)}"


def format_annotation(obj: Any) -> str:
    origin = typing.get_origin(obj)
    args = typing.get_args(obj)

    # special formatting for typing modules
    if origin is typing.Union and len(args) == 2 and args[1] is type(None):
        return f"Optional[{format_annotation(args[0])}]"

    elif origin in _known_typing_origins:
        origin_name = _known_typing_origins[origin]
        formatted_args = ", ".join(format_annotation(arg) for arg in args)

        return f"{origin_name}[{formatted_args}]"

    elif isinstance(obj, typing.TypeVar):
        return str(obj)

    elif isinstance(obj, collections.abc.Hashable) and obj in _known_objects:
        return _known_objects[obj]

    elif isinstance(obj, list):
        return "[{}]".format(", ".join(format_annotation(item) for item in obj))

    elif (
        hasattr(obj, "__module__")
        and hasattr(obj, "__name__")
        and obj.__module__ != "builtins"
    ):
        return f"{obj.__module__}.{obj.__name__}"

    elif hasattr(obj, "__name__"):
        return str(obj.__name__)

    else:
        return str(obj)


_known_typing_origins = {
    collections.abc.Callable: "Callable",
    collections.abc.Iterable: "Iterable",
    collections.abc.Mapping: "Mapping",
    collections.abc.Sequence: "Sequence",
    typing.Union: "Union",
    tuple: "Tuple",
    list: "List",
    dict: "Dict",
}

_known_objects = {
    typing.Any: "Any",
    callable: "callable",
}


# pytest plugin
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "minidoc(object): mark a test function running minicoc tests."
    )


def pytest_generate_tests(metafunc):
    if (mark := metafunc.definition.keywords.get("minidoc")) is not None:
        if "test" not in metafunc.fixturenames:
            raise RuntimeError("minidoc tests must take `test` as an argument")

        if len(mark.args) != 1 or len(mark.kwargs):
            raise RuntimeError(
                "The minidoc mark must be called with a single positional argument"
            )

        module_name = mark.args[0]
        module = importlib.import_module(module_name)

        tests = [(module_name, test) for test in get_doc_tests(module)]
        for child_name, child in get_module_contents(module):
            tests.extend(
                (f"{module_name}.{child_name}", block) for block in get_doc_tests(child)
            )

        metafunc.parametrize(
            "test",
            [build_doc_test_function(code) for _, code in tests],
            ids=[test_id for test_id, _ in tests],
        )


def get_doc_tests(obj):
    doc = inspect.getdoc(obj)

    if doc is None:
        return

    current = None
    in_code_block = False

    for line in doc.splitlines():
        if line.startswith("```python") and "ignore" not in line:
            assert not in_code_block

            current = []
            in_code_block = True

        elif line.startswith("```"):
            if in_code_block:
                if current:
                    yield "\n".join(current)

                in_code_block = False
                current = None

            else:
                assert current is None
                in_code_block = None

        elif in_code_block:
            assert current is not None
            if line.startswith(":"):
                line = line[2:]

            current.append(line)

    if current:
        raise RuntimeError("Unclosed code block")


def build_doc_test_function(code):
    def test():
        exec(code, {}, {})

    return test


if __name__ == "__main__":
    import argparse

    _parser = argparse.ArgumentParser()
    _parser.add_argument("files", type=pathlib.Path, nargs="+")

    _args = _parser.parse_args()

    for path in _args.files:
        update_docs(path)
