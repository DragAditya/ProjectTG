"""Basic tests for the Telegram Group Management Bot.

This test file ensures that all Python modules in the project can be
compiled without syntax errors.  It does not import external
dependencies, allowing the tests to run in environments where optional
packages are not installed.  If a module fails to compile, the test
will fail and display the error.
"""
import pathlib
import py_compile


def test_compile_all_sources() -> None:
    """Compile all Python files under the project root to check syntax."""
    root = pathlib.Path(__file__).resolve().parents[1] / "bot"
    for path in root.rglob("*.py"):
        try:
            py_compile.compile(path, doraise=True)
        except py_compile.PyCompileError as exc:
            raise AssertionError(f"Failed to compile {path}: {exc}")