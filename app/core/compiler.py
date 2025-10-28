# app/core/compiler.py
import subprocess
import os
from typing import Dict, Any, Optional
from app.utils.file import write_file, read_file

SUPPORTED_COMPILERS = {
    "c": ("gcc", ["-o", "out"]),
    "cpp": ("g++", ["-o", "out"]),
    "rust": ("rustc", ["-o", "out"]),
    "go": ("go", ["build", "-o", "out"]),
    "java": ("javac", []),
}

def compile_code(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compile code in any supported language.
    Returns binary path or error.
    """
    lang = task.get("language", "").lower()
    code = task.get("code", "")
    filename = f"temp_source.{get_extension(lang)}"

    if lang not in SUPPORTED_COMPILERS:
        return {"compiled": False, "error": f"Compiler for {lang} not available"}

    write_file(filename, code)

    compiler, flags = SUPPORTED_COMPILERS[lang]
    cmd = [compiler] + flags + [filename] if flags else [compiler, filename]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30
    )

    success = result.returncode == 0
    output_path = "out" if success and lang in ["c", "cpp", "rust", "go"] else None

    return {
        "compiled": success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "executable": output_path,
        "language": lang
    }

def get_extension(lang: str) -> str:
    return {
        "c": "c", "cpp": "cpp", "rust": "rs", "go": "go",
        "java": "java", "python": "py", "javascript": "js"
    }.get(lang, "txt")
