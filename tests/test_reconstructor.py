# tests/test_reconstructor.py
import pytest
import os
from unittest.mock import patch, MagicMock
from app.core.reconstructor import reconstruct_repo
from app.utils.git import clone_repo, commit_and_push

class TestRepoReconstructor:
    """Full GitHub repo reconstruction tests."""

    @pytest.fixture
    def mock_files(self, temp_dir):
        """Create mock repo structure."""
        write_file(os.path.join(temp_dir, "app.py"), "def hello(): pass")
        write_file(os.path.join(temp_dir, "utils/helper.js"), "function help() {}")
        return temp_dir

    @patch('app.core.reconstructor.transpile')
    @patch('app.utils.git.commit_and_push')
    def test_full_reconstruction(self, mock_push, mock_transpile, temp_dir, mock_git):
        """Complete repo → new language reconstruction."""
        # Setup
        mock_git.return_value = temp_dir
        mock_transpile.return_value = {"code": "// Transpiled code", "status": "transpiled"}
        mock_push.return_value = "https://github.com/strive/reconstructed"

        task = {
            "github_url": "https://github.com/example/app",
            "language": "rust",
            "modifications": ["add logging"]
        }

        result = reconstruct_repo(task)

        # Assertions
        assert result["status"] == "reconstructed"
        assert result["language"] == "rust"
        assert result["new_repo"] == "https://github.com/strive/reconstructed"
        assert result["files_transpiled"] >= 2
        mock_transpile.assert_called()

    def test_language_detection(self, temp_dir):
        """Detect source language from extension."""
        write_file(os.path.join(temp_dir, "main.py"), "print('py')")
        write_file(os.path.join(temp_dir, "script.js"), "console.log('js')")
        
        from app.core.reconstructor import _detect_lang
        assert _detect_lang(".py", "") == "python"
        assert _detect_lang(".js", "") == "javascript"

    @patch('app.core.reconstructor.transpile')
    def test_modification_application(self, mock_transpile, temp_dir):
        """Test modification injection."""
        original_code = "def api(): pass"
        write_file(os.path.join(temp_dir, "api.py"), original_code)
        
        task = {
            "github_url": "fake",
            "language": "python",
            "modifications": ["add auth"]
        }
        
        mock_transpile.return_value = {"code": original_code}
        result = reconstruct_repo(task)
        
        # Check that modifications were applied
        assert "AUTH ADDED" in result["code"]

    def test_code_file_filtering(self):
        """Only process code files."""
        from app.core.reconstructor import _is_code_file
        assert _is_code_file("app.py") is True
        assert _is_code_file("config.json") is False
        assert _is_code_file("README.md") is False

    def test_clone_failure(self, mock_git):
        """Handle failed repo clone."""
        mock_git.return_value = None
        
        task = {"github_url": "invalid", "language": "rust"}
        result = reconstruct_repo(task)
        assert "error" in result

    def test_no_transpile_same_language(self, temp_dir, mock_git):
        """Skip transpilation if languages match."""
        write_file(os.path.join(temp_dir, "app.py"), "print('test')")
        mock_git.return_value = temp_dir
        
        task = {"github_url": "fake", "language": "python"}
        with patch('app.core.reconstructor.transpile') as mock_transpile:
            reconstruct_repo(task)
            mock_transpile.assert_not_called()

@pytest.mark.asyncio
async def test_reconstruct_speed():
    """Reconstruction completes under 5s."""
    import time
    start = time.time()
    task = {"github_url": "https://github.com/example/small", "language": "go"}
    result = reconstruct_repo(task)
    assert time.time() - start < 5.0
