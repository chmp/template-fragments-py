"""Generate rust tests"""
# ruff: noqa: F541
import functools as ft
import json
import tomli

from pathlib import Path

self_path = Path(__file__).parent.resolve()


def main():
    dst = self_path / ".." / "tests" / "test_generated.py"

    print(":: update", dst)
    with open(dst, "wt") as fobj_dst:
        p = ft.partial(print, file=fobj_dst)

        p("import pytest")
        p()
        p("from template_fragments import split_templates, filter_template")
        p()
        p()
        p("def concat(*p: str) -> str:")
        p('    return "".join(p)')
        p()

        for p in self_path.glob("*.toml"):
            with p.open("rb") as fobj:
                spec = tomli.load(fobj)

            for test in spec["test"]:
                generate_test(test, fobj=fobj_dst)

    print("done")


def generate_test(test, *, fobj):
    p = ft.partial(print, file=fobj)
    newline = "\n"

    test_func_name = test["name"].replace(" ", "_")

    for mark in test.get("mark", []):
        p(f"@pytest.mark.{mark}")

    p(f"def test_{test_func_name}():")
    p(f"    template = concat(")
    for line in test["source"].splitlines():
        p(f"        {json.dumps(line.rstrip() + newline)},")
    p(f"    )")

    if any("expected" in test for test in test["fragment"]):
        p(f"    expected = {{")
        for fragment in test["fragment"]:
            p(f"        {json.dumps(fragment['name'])}: concat(")
            for line in fragment["expected"].splitlines():
                p(f"            {json.dumps(line.rstrip() + newline)},")
            p(f"        ),")
        p(f"    }}")

    if not test.get("error", False):
        for fragment in test["fragment"]:
            p(
                f"    assert filter_template(template, "
                f"{json.dumps(fragment['name'])}) "
                f" == expected[{json.dumps(fragment['name'])}]"
            )

        p("    assert split_templates(template) == expected")

    else:
        for fragment in test["fragment"]:
            p(f"    with pytest.raises(Exception):")
            p(f"        filter_template(template, {json.dumps(fragment['name'])})")

        p("    with pytest.raises(Exception):")
        p("        split_templates(template)")

    p()
    p()


if __name__ == "__main__":
    main()
