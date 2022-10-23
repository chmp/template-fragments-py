import re

from typing import Dict, Iterable, List, Optional, Set, Tuple, TypeVar

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")

fragment_tag = re.compile(
    r"(?P<head>[^\{]*)\{%\s+(?P<tag>fragment|endfragment)(?P<data>[^%]+)%\}(?P<tail>.*)"
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


def split_template(src: str) -> Dict[str, str]:
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

    for line in src.split("\n"):
        tag, data = parse_fragment_tag(line)
        if tag == "fragment":
            if reentrant := data & active_fragments:
                raise TemplateFragmentError(f"Reentrant fragments: {reentrant}")

            stack.append(data)
            active_fragments.update(data)
            seen_fragments.update(data)

        elif tag == "endfragment":
            active_fragments = active_fragments - stack.pop()

        else:
            yield active_fragments, line

    # append a trailing newline for fragments
    yield seen_fragments, ""


def parse_fragment_tag(s) -> Tuple[Optional[str], Set[str]]:
    if (m := fragment_tag.match(s)) is not None:
        if m.group("head").strip() or m.group("tail").strip():
            raise TemplateFragmentError()

        tag = m.group("tag")
        data = {item.strip() for item in m.group("data").split()}

        if tag == "fragment" and not data:
            raise TemplateFragmentError("fragment start tag without fragment names")

        elif tag == "endfragment" and data:
            raise TemplateFragmentError("fragment end tag with fragment names")

        return tag, data

    else:
        return None, []


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
