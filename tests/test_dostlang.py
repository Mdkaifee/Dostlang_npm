import pytest

from worklib import DostLangRuntimeError, run_source


def test_print_and_math() -> None:
    code = """
yeh_ha a = 10
yeh_ha b = 5
dost_bol a + b * 2
"""
    result = run_source(code)
    assert result.output == ["20"]


def test_if_else_branching() -> None:
    code = """
yeh_ha score = 73
agar score >= 80 {
  dost_bol "top"
} warna {
  dost_bol "improve"
}
"""
    result = run_source(code)
    assert result.output == ["improve"]


def test_while_loop() -> None:
    code = """
yeh_ha x = 1
jabtak x <= 3 {
  dost_bol x
  x = x + 1
}
"""
    result = run_source(code)
    assert result.output == ["1", "2", "3"]
    assert result.variables["x"] == 4


def test_reassign_requires_declaration() -> None:
    code = "x = 2"
    with pytest.raises(DostLangRuntimeError):
        run_source(code)


def test_comments_are_ignored() -> None:
    code = """
# this is a comment
yeh_ha x = 7  # inline comment
dost_bol x
"""
    result = run_source(code)
    assert result.output == ["7"]
