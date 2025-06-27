import pytest
import replace_placeholders


@pytest.fixture
def temp_readme_and_code(tmp_path):
    # Create a temp code file
    code_file = tmp_path / "code.py"
    code_file.write_text("a = 1\nb = 2\nc = 3\nd = 4\ne = 5\n")
    # Create a temp README file
    readme_file = tmp_path / "README.md"
    return tmp_path, readme_file, code_file


@pytest.mark.parametrize(
    "readme_content, expect_in, expect_not_in, expect_exit",
    [
        # Whole file inclusion
        (
            """
```python file={code_file}
PLACEHOLDER
```
""",
            ["a = 1", "e = 5"],
            ["PLACEHOLDER"],
            False,
        ),
        # Partial file inclusion
        (
            """
```python file={code_file} line_start=2 line_end=4
PLACEHOLDER
```
""",
            ["b = 2", "d = 4"],
            ["a = 1", "e = 5", "PLACEHOLDER"],
            False,
        ),
        # Nonexistent file
        (
            """
```python file=not_a_real_file.py
PLACEHOLDER
```
""",
            [],
            [],
            True,
        ),
        # Out of bounds lines
        (
            """
```python file={code_file} line_start=10 line_end=20
PLACEHOLDER
```
""",
            [],
            [],
            True,
        ),
        # Multiple placeholders
        (
            """
```python file={code_file} line_start=1 line_end=2
PLACEHOLDER1
```
Some text in between
```python file={code_file} line_start=4 line_end=5
PLACEHOLDER2
```
""",
            ["a = 1", "d = 4"],
            ["PLACEHOLDER1", "PLACEHOLDER2"],
            False,
        ),
        # Text before and after code block
        (
            """
Text before
```python file={code_file} line_start=2 line_end=3
PLACEHOLDER
```
Text after
""",
            ["b = 2", "Text before", "Text after"],
            ["PLACEHOLDER"],
            False,
        ),
        # Only code block, no placeholder (should not change)
        (
            """
```python file={code_file} line_start=2 line_end=3
b = 2
```
""",
            ["b = 2"],
            [],
            False,
        ),
        # Empty code block
        (
            """
```python file={code_file} line_start=2 line_end=1
PLACEHOLDER
```
""",
            [],
            [],
            True,
        ),
        # Code block with missing file attribute
        (
            """
```python
PLACEHOLDER
```
""",
            [],
            [],
            True,
        ),
        # Code block with negative line numbers
        (
            """
```python file={code_file} line_start=-1 line_end=2
PLACEHOLDER
```
""",
            [],
            [],
            True,
        ),
        # Code block with line_end before line_start
        (
            """
```python file={code_file} line_start=4 line_end=2
PLACEHOLDER
```
""",
            [],
            [],
            True,
        ),
    ],
)
def test_replace_placeholders_cases(
    temp_readme_and_code, readme_content, expect_in, expect_not_in, expect_exit
):
    tmp_path, readme_file, code_file = temp_readme_and_code
    content = readme_content.format(code_file=code_file)
    readme_file.write_text(content)
    if expect_exit:
        with pytest.raises(SystemExit):
            replace_placeholders.update_file(readme_file)
    else:
        replace_placeholders.update_file(readme_file)
        updated = readme_file.read_text()
        for s in expect_in:
            assert s in updated
        for s in expect_not_in:
            assert s not in updated
