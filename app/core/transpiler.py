# app/core/transpiler.py
import re
from typing import Dict, Any, Tuple

# Hand-crafted, deterministic, bidirectional transpilation rules
# No ML. No heuristics. Pure symbolic transformation.
TRANSPILE_RULES = {
    ("python", "javascript"): {
        r'\bprint\((.*)\)': r'console.log(\1)',
        r'def (\w+)\((.*)\):': r'function \1(\2) {',
        r'\bTrue\b': 'true',
        r'\bFalse\b': 'false',
        r'\bNone\b': 'null',
        r'(\w+) = (.*)': r'let \1 = \2;',
        r'if (.*):': r'if (\1) {',
        r'elif (.*):': r'} else if (\1) {',
        r'else:': r'} else {',
    },
    ("javascript", "python"): {
        r'console\.log\((.*)\)': r'print(\1)',
        r'function (\w+)\((.*)\) {': r'def \1(\2):',
        r'\btrue\b': 'True',
        r'\bfalse\b': 'False',
        r'\bnull\b': 'None',
        r'let (\w+) = (.*);': r'\1 = \2',
        r'if \((.*)\) {': r'if \1:',
        r'} else if \((.*)\) {': r'elif \1:',
        r'} else {': r'else:',
    }
}

INDENT_MAP = {
    ("python", "javascript"): ("    ", "  "),
    ("javascript", "python"): ("  ", "    ")
}

def transpile(task: Dict[str, Any]) -> Dict[str, Any]:
    src = task.get("from", "").lower()
    dst = task.get("to", "").lower()
    code = task.get("code", "")

    key = (src, dst)
    if key not in TRANSPILE_RULES:
        return {"error": f"Transpilation {src} → {dst} not supported"}

    rules = TRANSPILE_RULES[key]
    new_code = code

    # Apply regex substitutions
    for pattern, repl in rules.items():
        new_code = re.sub(pattern, repl, new_code)

    # Fix indentation
    src_indent, dst_indent = INDENT_MAP.get(key, ("", ""))
    if src_indent and dst_indent:
        lines = new_code.split('\n')
        fixed = []
        for line in lines:
            stripped = line.lstrip()
            indent_count = len(line) - len(stripped)
            new_indent = dst_indent * (indent_count // len(src_indent))
            fixed.append(new_indent + stripped)
        new_code = '\n'.join(fixed)

    # Close blocks for JS
    if src == "python" and dst == "javascript":
        new_code = re.sub(r'(\n)(?![\s}])', r'\1}\n', new_code)

    return {
        "code": new_code,
        "from": src,
        "to": dst,
        "status": "transpiled"
    }
