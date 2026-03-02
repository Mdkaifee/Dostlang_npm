from worklib import slugify, title_case


def test_slugify_removes_symbols_and_spaces() -> None:
    assert slugify("Hello, Python Library!") == "hello-python-library"


def test_title_case_squashes_spaces() -> None:
    assert title_case("hello    python   library") == "Hello Python Library"
