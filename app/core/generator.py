# ai_code_generator.py
"""
Professional AI Code Generator
================================
- Zero templates
- Pure Python string construction
- Enterprise security & validation
- Plugin architecture
- Type-safe, documented, testable
- Ready for LLM integration
"""

from __future__ import annotations

import re
import json
import uuid
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, TypeVar, Generic, Protocol
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# --------------------------------------------------------------------------- #
# Logging Configuration
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("AI_CODE_GENERATOR")


# --------------------------------------------------------------------------- #
# Enums & Protocols
# --------------------------------------------------------------------------- #
class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    BASH = "bash"
    GO = "go"
    RUST = "rust"


class GeneratorType(str, Enum):
    WEB_API = "web_api"
    CLI_TOOL = "cli_tool"
    EXPLOIT_DEMO = "exploit_demo"
    GAME = "game"
    DATA_PIPELINE = "data_pipeline"
    ML_MODEL = "ml_model"


class CodeResult(Protocol):
    code: str
    language: Language
    purpose: str
    generator: GeneratorType
    tests: List[str]
    runnable: bool
    dependencies: List[str]
    filename: str
    metadata: Dict[str, Any]


# --------------------------------------------------------------------------- #
# Security & Validation
# --------------------------------------------------------------------------- #
class CodeSecurityValidator:
    """Validates generated code for security risks."""

    BLACKLISTED_IMPORTS = {
        "os", "subprocess", "sys", "shutil", "pickle", "ctypes", "socket", "threading"
    }
    BLACKLISTED_FUNCTIONS = {
        "exec", "eval", "compile", "__import__", "open", "system", "popen"
    }

    @staticmethod
    def validate(code: str, allow_network: bool = False) -> List[str]:
        issues = []

        # Check imports
        for imp in CodeSecurityValidator.BLACKLISTED_IMPORTS:
            if re.search(rf"\bimport\s+{imp}\b", code) or re.search(rf"\bfrom\s+{imp}\b", code):
                if imp == "socket" and allow_network:
                    continue
                issues.append(f"Blocked import: {imp}")

        # Check dangerous functions
        for func in CodeSecurityValidator.BLACKLISTED_FUNCTIONS:
            if re.search(rf"\b{func}\s*\(", code):
                issues.append(f"Blocked function call: {func}")

        # Check shell injection
        if re.search(r"!\s*[`'\"]", code) or re.search(r"subprocess\.call\s*\(", code):
            issues.append("Potential shell injection")

        return issues


# --------------------------------------------------------------------------- #
# Core Generator Interface
# --------------------------------------------------------------------------- #
T = TypeVar("T")

@dataclass
class GenerationContext(Generic[T]):
    task: Dict[str, Any]
    config: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class CodeGeneratorPlugin(ABC, Generic[T]):
    """Base class for all code generators."""

    @property
    @abstractmethod
    def generator_type(self) -> GeneratorType:
        ...

    @property
    @abstractmethod
    def supported_languages(self) -> List[Language]:
        ...

    @abstractmethod
    def generate(self, ctx: GenerationContext[T]) -> CodeResult:
        ...

    def validate_task(self, task: Dict[str, Any]) -> None:
        """Override to validate input task."""
        pass

    def post_process(self, result: CodeResult) -> CodeResult:
        """Hook for final cleanup."""
        return result


# --------------------------------------------------------------------------- #
# Python Generators
# --------------------------------------------------------------------------- #
class PythonWebAPIGenerator(CodeGeneratorPlugin[None]):
    generator_type = GeneratorType.WEB_API
    supported_languages = [Language.PYTHON]

    def _build_model(self, name: str, fields: List[Dict]) -> List[str]:
        lines = [f"class {name}(BaseModel):"]
        for f in fields:
            lines.append(f"    {f['name']}: {f.get('type', 'str')}")
        return lines

    def generate(self, ctx: GenerationContext[None]) -> CodeResult:
        task = ctx.task
        name = task.get("name", "API")
        endpoint = task.get("endpoint", "process")
        model_name = task.get("request_class", "Request")
        fields = task.get("fields", [{"name": "data", "type": "str"}])

        lines = [
            "from fastapi import FastAPI",
            "from pydantic import BaseModel",
            "",
            f"app = FastAPI(title=\"{name}\")",
            "",
        ]
        lines.extend(self._build_model(model_name, fields))
        lines += [
            "",
            f"@app.post(\"/{endpoint}\")",
            f"def {endpoint}(data: {model_name}):",
            "    return {\"status\": \"ok\", \"data\": data.dict()}",
        ]

        code = "\n".join(lines)
        issues = CodeSecurityValidator.validate(code)
        if issues:
            logger.warning(f"Security issues in {self.generator_type}: {issues}")

        return {
            "code": code,
            "language": Language.PYTHON,
            "purpose": task.get("purpose", "web_api"),
            "generator": self.generator_type,
            "tests": self._tests(endpoint),
            "runnable": True,
            "dependencies": ["fastapi", "pydantic", "uvicorn[standard]"],
            "filename": f"{name.lower()}_api.py",
            "metadata": {"request_id": ctx.request_id, "issues": issues},
        }

    def _tests(self, endpoint: str) -> List[str]:
        return [
            "def test_model():",
            "    from pydantic import ValidationError",
            "    # Add validation tests",
            "",
            f"def test_endpoint():",
            "    from fastapi.testclient import TestClient",
            "    client = TestClient(app)",
            f"    resp = client.post('/{endpoint}', json={{}})",
            "    assert resp.status_code == 200",
        ]


class PythonCLIToolGenerator(CodeGeneratorPlugin[None]):
    generator_type = GeneratorType.CLI_TOOL
    supported_languages = [Language.PYTHON]

    def generate(self, ctx: GenerationContext[None]) -> CodeResult:
        task = ctx.task
        name = task.get("name", "tool")
        desc = task.get("description", "CLI tool")
        raw_args = task.get("args", [])

        args = []
        for a in raw_args:
            flag = a.get("flag", "--input")
            name_arg = a.get("name") or re.sub(r"^-+", "", flag).replace("-", "_")
            args.append({
                "flag": flag,
                "name": name_arg,
                "type": a.get("type_py", "str"),
                "help": a.get("help", ""),
                "required": bool(a.get("required")),
            })

        lines = [
            "import argparse",
            "import sys",
            "",
            "def main() -> int:",
            f"    parser = argparse.ArgumentParser(description=\"{desc}\")",
        ]

        for a in args:
            dest = f", dest=\"{a['name']}\"" if a['name'] != re.sub(r"^-+", "", a['flag']).replace("-", "_") else ""
            req = ", required=True" if a['required'] else ""
            lines.append(f"    parser.add_argument(\"{a['flag']}\"{dest}, type={a['type']}, help=\"{a['help']}\"{req})")

        lines += [
            "    args = parser.parse_args()",
            f"    print(f\"Running {name}...\")",
        ]
        for a in args:
            lines.append(f"    print(f\"  {a['name']} = {{getattr(args, '{a['name']}')}}\")")

        lines += ["    return 0", "", "if __name__ == \"__main__\":", "    sys.exit(main())"]

        code = "\n".join(lines)

        return {
            "code": code,
            "language": Language.PYTHON,
            "purpose": "cli",
            "generator": self.generator_type,
            "tests": self._tests(),
            "runnable": True,
            "dependencies": [],
            "filename": f"{name.lower()}.py",
            "metadata": {"request_id": ctx.request_id},
        }

    def _tests(self) -> List[str]:
        return [
            "def test_help():",
            "    import subprocess",
            "    r = subprocess.run(['python', 'tool.py', '--help'], capture_output=True, text=True)",
            "    assert r.returncode == 0",
        ]


# --------------------------------------------------------------------------- #
# Generator Registry
# --------------------------------------------------------------------------- #
class GeneratorRegistry:
    _plugins: Dict[GeneratorType, CodeGeneratorPlugin] = {}

    @classmethod
    def register(cls, plugin: CodeGeneratorPlugin):
        cls._plugins[plugin.generator_type] = plugin
        logger.info(f"Registered generator: {plugin.generator_type}")

    @classmethod
    def get(cls, gtype: GeneratorType) -> CodeGeneratorPlugin:
        if gtype not in cls._plugins:
            raise ValueError(f"No generator for {gtype}")
        return cls._plugins[gtype]

    @classmethod
    def list(cls) -> List[GeneratorType]:
        return list(cls._plugins.keys())


# Register built-in generators
GeneratorRegistry.register(PythonWebAPIGenerator())
GeneratorRegistry.register(PythonCLIToolGenerator())


# --------------------------------------------------------------------------- #
# AI Code Generator Engine
# --------------------------------------------------------------------------- #
@dataclass
class AICodeGenerator:
    """Main entry point for AI-powered code generation."""

    registry: GeneratorRegistry = field(default_factory=GeneratorRegistry)

    def generate(self, task: Dict[str, Any]) -> CodeResult:
        purpose = task.get("purpose", "").lower()
        lang = Language(task.get("language", "python").lower())

        # Route by purpose
        if "api" in purpose or "web" in purpose:
            gtype = GeneratorType.WEB_API
        elif "cli" in purpose or "tool" in purpose:
            gtype = GeneratorType.CLI_TOOL
        else:
            raise ValueError(f"Unknown purpose: {purpose}")

        plugin = self.registry.get(gtype)
        if lang not in plugin.supported_languages:
            raise ValueError(f"{gtype} does not support {lang}")

        ctx = GenerationContext(task=task)
        result = plugin.generate(ctx)
        return plugin.post_process(result)

    def generate_from_prompt(self, prompt: str) -> CodeResult:
        """Parse natural language prompt into task (LLM-ready)."""
        # In production: use LLM to extract structured task
        task = {
            "purpose": "web api",
            "name": "MyAPI",
            "endpoint": "hello",
            "fields": [{"name": "name", "type": "str"}]
        }
        return self.generate(task)


# --------------------------------------------------------------------------- #
# CLI & Export
# --------------------------------------------------------------------------- #
def save_result(result: CodeResult, output_dir: Path = Path("generated")):
    output_dir.mkdir(exist_ok=True)
    code_path = output_dir / result["filename"]
    test_path = output_dir / f"test_{result['filename']}"

    code_path.write_text(result["code"])
    if result["tests"]:
        test_path.write_text("\n\n".join(result["tests"]))

    logger.info(f"Generated: {code_path}")
    if result["dependencies"]:
        req_path = output_dir / "requirements.txt"
        req_path.write_text("\n".join(result["dependencies"]) + "\n")
        logger.info(f"Dependencies: {req_path}")


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
generator = AICodeGenerator()


def generate_code(task: Dict[str, Any]) -> CodeResult:
    """High-level API for code generation."""
    return generator.generate(task)


# --------------------------------------------------------------------------- #
# Example Usage
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    task = {
        "purpose": "web api",
        "name": "UserService",
        "endpoint": "create",
        "request_class": "UserCreate",
        "fields": [
            {"name": "username", "type": "str"},
            {"name": "email", "type": "str"},
            {"name": "age", "type": "int"}
        ]
    }

    result = generate_code(task)
    save_result(result)

    print("\n--- GENERATED CODE ---")
    print(result["code"])
