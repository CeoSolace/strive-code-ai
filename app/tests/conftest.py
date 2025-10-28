# tests/conftest.py
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from app.core.engine import StriveCodeEngine
from app.utils.git import clone_repo
from app.utils.file import write_file

@pytest.fixture
def engine():
    """Fresh StriveCodeEngine instance."""
    return StriveCodeEngine()

@pytest.fixture
def temp_dir():
    """Temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def mock_git():
    """Mock git operations."""
    with patch('app.utils.git.clone_repo') as mock:
        mock.return_value = '/tmp/mock_repo'
        yield mock

@pytest.fixture
def sample_code():
    """Sample Python code for testing."""
    return """
def hello_world(name):
    if name:
        print(f"Hello, {name}!")
    else:
        print("Hello, World!")
    return True
"""

@pytest.fixture
def sample_js_code():
    """Sample JavaScript code."""
    return """
function helloWorld(name) {
    if (name) {
        console.log(`Hello, ${name}!`);
    } else {
        console.log("Hello, World!");
    }
    return true;
}
"""

@pytest.fixture
def test_repo_url():
    """Mock GitHub repo URL."""
    return "https://github.com/example/test-repo"
