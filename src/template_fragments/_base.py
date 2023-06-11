import re

from typing import Dict, Iterable, List, Optional, Set, Tuple, TypeVar

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")

fragment_tag = re.compile(
    r"(?P<head>[^\{]*)\{%\s+(?P<tag>[^\s]+)(?P<data>[^%]+)%\}(?P<tail>.*)"
)


def split_path(path: str) -> Tuple[str, str]:
    """Split the fragment from the path"""
    template, _, fragment = path.rpartition("#")
    return (template, fragment) if template else (fragment, "")


def filter_template(src: str, fragment: str = "") -> str:
    """Return the parts of the template for the given fragment

    Parameters:

    - `src`: the template source
    - `fragment`: the fragment to return. If `fragment = ""`, removes any
      fragment directives
    """
    return "\n".join(
        line
        for active_fragments, line in _split_impl(src)
        if fragment in active_fragments
    )


def split_templates(src: str) -> Dict[str, str]:
    """Return all fragments contained in the template

    The key `""` gives the source template with any fragment directives removed.
    """
    fragment_lines = collect(
        (fragment, line)
        for active_fragments, line in _split_impl(src)
        for fragment in active_fragments
    )

    return {fragment: "\n".join(lines) for fragment, lines in fragment_lines}


def _split_impl(src: str) -> Iterable[Tuple[Set[str], str]]:
    stack: List[List[str]] = []
    active_fragments: Set[str] = {""}
    seen_fragments: Set[str] = set()

    line_idx = 0
    for line_idx, line in enumerate(src.split("\n")):
        tag, head, data = parse_fragment_tag(line, line_idx)
        if tag == "fragment":
            if reentrant := data & active_fragments:
                raise TemplateFragmentError(
                    f"Reentrant fragments: {reentrant} in line {line_idx + 1}"
                )

            stack.append(data)
            active_fragments.update(data)
            seen_fragments.update(data)

        elif tag == "endfragment":
            if not stack:
                raise TemplateFragmentError(
                    f"Unbalanced fragments in line {line_idx + 1}"
                )

            active_fragments = active_fragments - stack.pop()

        elif tag == "fragment-block":
            if reentrant := data & active_fragments:
                raise TemplateFragmentError(
                    f"Reentrant fragments: {reentrant} in line {line_idx + 1}"
                )

            stack.append(data)
            active_fragments.update(data)
            seen_fragments.update(data)

            (block_name,) = data
            yield active_fragments, f"{head}{{% block {block_name} %}}"

        elif tag == "endfragment-block":
            yield active_fragments, f"{head}{{% endblock %}}"
            active_fragments = active_fragments - stack.pop()

        else:
            yield active_fragments, line

    # append a trailing newline for fragments
    yield seen_fragments, ""

    if stack:
        raise TemplateFragmentError(f"Unbalanced fragments in line {line_idx + 1}")


def parse_fragment_tag(s, line_idx) -> Tuple[Optional[str], Set[str]]:
    if (m := fragment_tag.match(s)) is not None:
        head = m.group("head")
        if head.strip() or m.group("tail").strip():
            raise TemplateFragmentError()

        tag = m.group("tag")
        data = {item.strip() for item in m.group("data").split()}

        if tag == "fragment" and not data:
            raise TemplateFragmentError(
                f"fragment start tag without fragment names in line {line_idx + 1}"
            )

        if tag in {"endfragment", "endfragment-block"} and data:
            raise TemplateFragmentError(
                f"fragment end tag with fragment names in line {line_idx + 1}"
            )

        if tag == "fragment-block" and len(data) != 1:
            raise TemplateFragmentError(
                "fragment-block start tag must have a single name in line "
                f"{line_idx + 1}"
            )

        return tag, head, data

    else:
        return None, "", []


def flatten(items: Iterable[Iterable[T]]) -> Iterable[T]:
    for item in items:
        yield from item


def collect(items: Iterable[Tuple[K, V]]) -> Iterable[Tuple[K, List[V]]]:
    res = {}
    for k, v in items:
        res.setdefault(k, []).append(v)
    return res.items()


class TemplateFragmentError(Exception):
    pass
