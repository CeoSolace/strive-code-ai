# app/core/teacher.py
from typing import Dict, Any
from app.core.multimodal import generate_voice, generate_jupyter

def explain(task: Dict[str, Any]) -> Dict[str, Any]:
    code = task.get("code", "")
    lang = task.get("language", "python")
    purpose = task.get("purpose", "unknown")

    explanation = f"""
# EXPLANATION OF {lang.upper()} CODE

**Purpose**: {purpose}

## Step-by-Step Breakdown

1. **Initialization** — Variables and imports are declared.
2. **Input Processing** — Data is read and validated.
3. **Core Logic** — The main algorithm runs.
4. **Output** — Results are formatted and returned.

## Key Concepts
- Control flow: `if`, `for`, `while`
- Data structures: lists, dicts, classes
- Functions: reusable logic blocks

## Best Practices Applied
- Clear naming
- Error handling
- Efficiency: O(n) time
"""

    return {
        "explanation": explanation.strip(),
        "voice": generate_voice({"text": explanation}),
        "notebook": generate_jupyter({"code": code, "explanation": explanation}),
        "language": lang,
        "complexity": "O(n log n)" if "sort" in code else "O(n)"
    }
