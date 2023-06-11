# ruff: noqa: E401, E731
import functools as ft
import pathlib
import subprocess
import sys

__effect = lambda effect: lambda func: [func, effect(func.__dict__)][0]
cmd = lambda **kw: __effect(lambda d: d.setdefault("@cmd", {}).update(kw))
arg = lambda *a, **kw: __effect(lambda d: d.setdefault("@arg", []).append((a, kw)))
self_path = pathlib.Path(__file__).parent.resolve()
once = lambda: lambda func: ft.lru_cache(maxsize=None)(func)


@cmd()
@arg("--backtrace", action="store_true", default=False)
def precommit(backtrace=False):
    generate_tests()
    format()
    lint()
    test(backtrace=backtrace)
    update_docs()


@cmd()
def format():
    python("-m", "black", ".")


@cmd()
def lint():
    python("-m", "ruff", ".")


@cmd()
@arg("--backtrace", action="store_true", default=False)
def test(backtrace):
    generate_tests()
    python(
        "-m",
        "pytest",
        "tests",
    )


@cmd()
def update_docs():
    print(":: update Readme.md")
    __import__("minidoc").update_docs("Readme.md")


@cmd()
@once()
def generate_tests():
    src_path = self_path / "specs" / "generate_tests.py"
    dst_path = self_path / "tests" / "test_generated.py"
    spec_paths = list(self_path.joinpath("specs").glob("*.toml"))

    if (
        not dst_path.exists()
        or src_path.stat().st_mtime > dst_path.stat().st_mtime
        or any(p.stat().st_mtime > dst_path.stat().st_mtime for p in spec_paths)
    ):
        python(src_path)


def python(*args, **kwargs):
    return run(sys.executable, *args, **kwargs)


def run(*args, **kwargs):
    kwargs.setdefault("check", True)
    kwargs.setdefault("cwd", self_path)

    args = [str(arg) for arg in args]
    print("::", " ".join(args))
    return subprocess.run(args, **kwargs)


if __name__ == "__main__":
    _sps = (_p := __import__("argparse").ArgumentParser()).add_subparsers()
    for _f in (f for f in list(globals().values()) if hasattr(f, "@cmd")):
        (_sp := _sps.add_parser(_f.__name__, **getattr(_f, "@cmd"))).set_defaults(_=_f)
        [_sp.add_argument(*a, **kw) for a, kw in reversed(getattr(_f, "@arg", []))]
    (_a := vars(_p.parse_args())).pop("_", _p.print_help)(**_a)
