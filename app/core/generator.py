# app/core/generator.py
import random
import string
from typing import Dict, Any, List
from jinja2 import Template
import os

# Symbolic code templates — no LLM, pure deterministic generation
CODE_TEMPLATES = {
    "web_api": """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="{{name}}")

class {{name}}Request(BaseModel):
    {% for field in fields %}
    {{field.name}}: {{field.type}}
    {% endfor %}

@app.post("/{{endpoint}}")
def {{endpoint}}(data: {{name}}Request):
    return {"result": "processed", "input": data}
""",
    "cli_tool": """
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="{{desc}}")
    {% for arg in args %}
    parser.add_argument("{{arg.flag}}", type={{arg.type}}, help="{{arg.help}}")
    {% endfor %}
    args = parser.parse_args()
    print("Running {{name}}...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
""",
    "exploit": """
# {{name}} — {{desc}}
# Target: {{target}}
# CVE: {{cve}}

payload = b"{{'A' * offset}}{{shellcode}}"
buffer = "OVERFLOW" + payload
print(f"[+] Sending {len(payload)} byte payload...")
""",
    "game": """
import pygame
pygame.init()

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    screen.fill((0, 0, 0))
    pygame.display.flip()
    clock.tick(60)
"""
}

def generate_code(task: Dict[str, Any]) -> Dict[str, Any]:
    purpose = task.get("purpose", "hello_world").lower()
    lang = task.get("language", "python").lower()
    constraints = task.get("constraints", [])

    if "web" in purpose and "api" in purpose:
        template_key = "web_api"
    elif "cli" in purpose or "tool" in purpose:
        template_key = "cli_tool"
    elif "exploit" in purpose or "payload" in purpose:
        template_key = "exploit"
    elif "game" in purpose:
        template_key = "game"
    else:
        template_key = "web_api"

    template_str = CODE_TEMPLATES.get(template_key, CODE_TEMPLATES["web_api"])
    template = Template(template_str)

    context = {
        "name": "".join(w.capitalize() for w in purpose.split()),
        "endpoint": purpose.replace(" ", "-"),
        "desc": purpose,
        "fields": [{"name": "input", "type": "str"}],
        "args": [{"flag": "--input", "type": "str", "help": "input data"}],
        "target": "192.168.1.1",
        "cve": "CVE-2025-0000",
        "offset": 1337,
        "shellcode": "\\x90\\x90\\xcc"
    }

    code = template.render(**context)

    return {
        "code": code.strip(),
        "language": lang,
        "purpose": purpose,
        "template": template_key,
        "tests": _generate_tests(code, lang),
        "runnable": True,
        "dependencies": _detect_deps(code, lang)
    }

def _generate_tests(code: str, lang: str) -> List[str]:
    if lang == "python":
        return [
            "def test_main(): assert True",
            "def test_api(): pass"
        ]
    return []

def _detect_deps(code: str, lang: str) -> List[str]:
    if "fastapi" in code:
        return ["fastapi", "uvicorn", "pydantic"]
    return []
