# tests/test_transpiler.py
import pytest
from app.core.transpiler import transpile

class TestTranspiler:
    """Bidirectional transpilation tests."""

    def test_python_to_js(self):
        """Python → JavaScript transpilation."""
        code = """
def greet(name):
    print(f"Hello, {name}!")
    return True
"""
        task = {
            "from": "python",
            "to": "javascript",
            "code": code
        }
        result = transpile(task)
        
        assert result["status"] == "transpiled"
        assert "function greet(name)" in result["code"]
        assert "console.log(`Hello, ${name}!`)" in result["code"]
        assert "return true;" in result["code"]

    def test_js_to_python(self):
        """JavaScript → Python transpilation."""
        code = """
function greet(name) {
    console.log(`Hello, ${name}!`);
    return true;
}
"""
        task = {
            "from": "javascript",
            "to": "python",
            "code": code
        }
        result = transpile(task)
        
        assert "def greet(name):" in result["code"]
        assert "print(f'Hello, {name}!')" in result["code"]
        assert "return True" in result["code"]

    def test_conditionals(self):
        """Test if/else transpilation."""
        py_code = """
if x > 0:
    print("positive")
else:
    print("negative")
"""
        task = {"from": "python", "to": "javascript", "code": py_code}
        result = transpile(task)
        
        assert 'if (x > 0) {' in result["code"]
        assert '} else {' in result["code"]

    def test_indentation(self):
        """Test indentation conversion."""
        code = """
def test():
    x = 1
    if x:
        y = 2
"""
        task = {"from": "python", "to": "javascript", "code": code}
        result = transpile(task)
        
        lines = result["code"].split("\n")
        assert "  x = 1;" in lines[2]
        assert "    y = 2;" in lines[4]

    def test_unsupported_direction(self):
        """Unsupported transpilation returns error."""
        task = {"from": "rust", "to": "go", "code": "fn main() {}"}
        result = transpile(task)
        assert "error" in result

    @pytest.mark.parametrize("pair", [
        ("python", "javascript"),
        ("javascript", "python"),
    ])
    def test_roundtrip(self, pair):
        """Python ↔ JS roundtrip preserves logic."""
        original = "print('test')"
        task1 = {"from": pair[0], "to": pair[1], "code": original}
        intermediate = transpile(task1)["code"]
        
        task2 = {"from": pair[1], "to": pair[0], "code": intermediate}
        final = transpile(task2)["code"]
        
        assert "print" in final
