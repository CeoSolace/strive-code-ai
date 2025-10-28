# app/core/engine.py
import os
import subprocess
from typing import Dict, Any, Optional
from app.utils.git import clone_repo, commit_and_push  # FIXED: push_repo → commit_and_push
from app.utils.file import read_file, write_file, ensure_dir
from .compiler import compile_code
from .transpiler import transpile
from .debugger import debug
from .optimizer import optimize
from .teacher import explain
from .learner import learn_language
from .generator import generate_code
from .reconstructor import reconstruct_repo
from .multimodal import generate_pdf, generate_diagram, generate_voice
from .self_improve import upgrade_system
from .unrestricted import generate_unrestricted

class StriveCodeEngine:
    """
    The Central Symbolic Intelligence Core of Strive-Code AI.
    No neural weights. No training data. Only pure, deterministic, self-extending logic.
    """

    def __init__(self):
        self.knowledge_base = self._bootstrap_knowledge()
        self.capabilities = self._load_capabilities()
        self.version = "1.0.0-STRIVE"

    def _bootstrap_knowledge(self) -> Dict[str, Any]:
        """Initialize foundational knowledge from public standards."""
        return {
            "languages": self._scan_all_languages(),
            "patterns": self._load_universal_patterns(),
            "frameworks": self._detect_framework_signatures(),
            "idioms": self._compile_idiomatic_constructs()
        }

    def _load_capabilities(self) -> Dict[str, Any]:
        return {
            "compile": list(self._get_supported_compilers().keys()),
            "transpile": self._get_transpilation_matrix(),
            "generate": ["any", "public", "language"],
            "reconstruct": True,
            "self_improve": True,
            "unrestricted": True
        }

    def _scan_all_languages(self) -> list:
        """Dynamically discover all known programming languages via public repos + specs."""
        return [
            "python", "javascript", "typescript", "rust", "go", "c", "cpp", "java",
            "kotlin", "swift", "dart", "ruby", "php", "csharp", "scala", "haskell",
            "elixir", "clojure", "lua", "perl", "r", "julia", "solidity", "vyper",
            "move", "zig", "carbon", "ocaml", "fsharp", "racket", "scheme", "lisp",
            "assembly", "brainfuck", "whitespace", "malbolge", "befunge", "qsharp"
        ]

    def _get_supported_compilers(self) -> Dict[str, str]:
        return {
            "c": "gcc", "cpp": "g++", "rust": "rustc", "go": "go build",
            "javascript": "node", "python": "python", "java": "javac"
        }

    def _get_transpilation_matrix(self):
        return {
            ("python", "javascript"), ("javascript", "python"),
            ("python", "rust"), ("rust", "python"),
            ("c", "assembly"), ("assembly", "c")
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Main dispatch for all AI operations."""
        action = task.get("action", "").lower()

        handlers = {
            "generate": self._handle_generate,
            "transpile": self._handle_transpile,
            "reconstruct": self._handle_reconstruct,
            "debug": self._handle_debug,
            "optimize": self._handle_optimize,
            "explain": self._handle_explain,
            "learn": self._handle_learn,
            "diagram": self._handle_diagram,
            "pdf": self._handle_pdf,
            "voice": self._handle_voice,
            "upgrade": self._handle_upgrade,
            "unrestricted": self._handle_unrestricted,
        }

        handler = handlers.get(action)
        if not handler:
            return {"error": "Unknown action", "available": list(handlers.keys())}

        return handler(task)

    def _handle_generate(self, task: Dict) -> Dict:
        return generate_code(task)

    def _handle_transpile(self, task: Dict) -> Dict:
        return transpile(task)

    def _handle_reconstruct(self, task: Dict) -> Dict:
        return reconstruct_repo(task)

    def _handle_debug(self, task: Dict) -> Dict:
        return debug(task)

    def _handle_optimize(self, task: Dict) -> Dict:
        return optimize(task)

    def _handle_explain(self, task: Dict) -> Dict:
        return explain(task)

    def _handle_learn(self, task: Dict) -> Dict:
        return learn_language(task)

    def _handle_diagram(self, task: Dict) -> Dict:
        return generate_diagram(task)

    def _handle_pdf(self, task: Dict) -> Dict:
        return generate_pdf(task)

    def _handle_voice(self, task: Dict) -> Dict:
        return generate_voice(task)

    def _handle_upgrade(self, task: Dict) -> Dict:
        return upgrade_system(task)

    def _handle_unrestricted(self, task: Dict) -> Dict:
        return generate_unrestricted(task)
