import black


def test_black_format_str():
    actual = black.format_str("def f(arg:str='')->None:...", mode=black.FileMode())
    expected = """def f(arg: str = "") -> None:
    ...
"""
    assert actual == expected
