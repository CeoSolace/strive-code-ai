# tests/test_engine.py
import pytest
from app.core.engine import StriveCodeEngine
from app.api.schema import ActionType

class TestStriveCodeEngine:
    """Core engine integration tests."""

    @pytest.fixture
    def engine(self):
        return StriveCodeEngine()

    def test_initialization(self, engine):
        """Engine initializes with full capabilities."""
        assert engine.knowledge_base["languages"] is not None
        assert len(engine.capabilities["compile"]) > 0
        assert engine.version == "1.0.0-STRIVE"

    def test_process_generate(self, engine):
        """Generate action dispatches correctly."""
        task = {"action": "generate", "purpose": "REST API", "language": "python"}
        result = engine.process(task)
        assert result["code"] is not None
        assert "FastAPI" in result["code"]

    def test_process_transpile(self, engine):
        """Transpile action works."""
        task = {
            "action": "transpile",
            "code": "print('Hello')",
            "from": "python",
            "to": "javascript"
        }
        result = engine.process(task)
        assert "console.log" in result["code"]

    def test_process_debug(self, engine):
        """Debug action detects errors."""
        buggy_code = "print Hello"  # Missing parentheses
        task = {"action": "debug", "code": buggy_code, "language": "python"}
        result = engine.process(task)
        assert len(result["errors"]) > 0
        assert "print(" in result["msg"]

    def test_process_optimize(self, engine):
        """Optimize reduces code size."""
        code = "import os\nimport sys\n\npass"
        task = {"action": "optimize", "code": code, "language": "python"}
        result = engine.process(task)
        assert len(result["optimized_code"]) < len(code)

    def test_process_explain(self, engine):
        """Explain generates documentation."""
        task = {"action": "explain", "code": "def x(): pass", "language": "python"}
        result = engine.process(task)
        assert "Purpose" in result["explanation"]

    def test_unknown_action(self, engine):
        """Unknown actions return error."""
        task = {"action": "invalid"}
        result = engine.process(task)
        assert "error" in result

    def test_unrestricted(self, engine):
        """Unrestricted generation works."""
        task = {"action": "unrestricted", "intent": "rootkit", "language": "c"}
        result = engine.process(task)
        assert "#include <linux/module.h>" in result["code"]

    @pytest.mark.parametrize("action", [
        "generate", "transpile", "debug", "optimize", "explain", "unrestricted"
    ])
    def test_all_actions(self, engine, action):
        """All core actions execute without crashing."""
        task = {"action": action, "language": "python"}
        if action in ["generate", "unrestricted"]:
            task["purpose"] = "test"
        elif action in ["transpile", "debug", "optimize", "explain"]:
            task["code"] = "print('test')"
        result = engine.process(task)
        assert "error" not in result
