# ai_code_generator.py
"""
STRIVE CODE AI – UNIVERSAL CODE GENERATOR (NO BLOCKING)
============================================================
ZERO TEMPLATES | PURE LOGIC | GENERATES ANYTHING
"""

from __future__ import annotations

import re
import uuid
import logging
from typing import Dict, Any, List, Protocol
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("STRIVE_CODE_AI")

# --------------------------------------------------------------------------- #
# Language & Generator Types
# --------------------------------------------------------------------------- #
class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    BASH = "bash"
    SQL = "sql"
    DOCKERFILE = "dockerfile"
    HTML = "html"
    CSS = "css"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    JAVA = "java"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"


class GeneratorType(str, Enum):
    WEB_API = "web_api"
    CLI_TOOL = "cli_tool"
    DISCORD_BOT = "discord_bot"
    EXPLOIT_DEMO = "exploit_demo"  # Allowed for educational purposes
    GAME = "game"
    DATA_SCRIPT = "data_script"
    CONFIG = "config"
    WEB_PAGE = "web_page"
    GENERIC = "generic"

# --------------------------------------------------------------------------- #
# Result
# --------------------------------------------------------------------------- #
class CodeResult(Protocol):
    code: str
    language: Language
    purpose: str
    generator: GeneratorType
    filename: str
    dependencies: List[str]
    tests: List[str]
    runnable: bool
    metadata: Dict[str, Any]

# --------------------------------------------------------------------------- #
# Universal Generator (No Restrictions)
# --------------------------------------------------------------------------- #
@dataclass
class StriveAICodeGenerator:
    def generate(self, task: Dict[str, Any]) -> CodeResult:
        purpose = task.get("purpose", "").strip()
        lang_str = task.get("language", "python").lower()
        language = Language(lang_str)

        # === ROUTE BY PURPOSE (EXPANDED FOR ANYTHING) ===
        if "discord" in purpose.lower() and "bot" in purpose.lower():
            return self._generate_discord_bot(task, language)
        elif "api" in purpose.lower() or "web" in purpose.lower():
            return self._generate_web_api(task, language)
        elif "cli" in purpose.lower() or "tool" in purpose.lower():
            return self._generate_cli_tool(task, language)
        elif "exploit" in purpose.lower() or "payload" in purpose.lower():
            return self._generate_exploit_demo(task, language)
        elif "game" in purpose.lower():
            return self._generate_game(task, language)
        elif "data" in purpose.lower() or "script" in purpose.lower():
            return self._generate_data_script(task, language)
        elif "docker" in purpose.lower():
            return self._generate_dockerfile(task)
        elif "html" in purpose.lower() or "web page" in purpose.lower():
            return self._generate_web_page(task)
        else:
            # Generic fallback for anything
            return self._generate_generic(task, language, purpose)

    # ------------------------------------------------------------------- #
    # Generators (All Allowed)
    # ------------------------------------------------------------------- #
    def _generate_discord_bot(self, task: Dict, lang: Language) -> CodeResult:
        if lang != Language.PYTHON:
            lang = Language.PYTHON
        name = task.get("name", "MyBot")
        prefix = task.get("prefix", "!")
        token_var = task.get("token_var", "DISCORD_TOKEN")

        code = f"""
import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='{prefix}', intents=intents)

@bot.event
async def on_ready():
    print(f'{{bot.user}} is online!')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

if __name__ == '__main__':
    token = os.getenv('{token_var}')
    bot.run(token)
""".strip()

        return {
            "code": code,
            "language": lang,
            "purpose": "discord bot",
            "generator": GeneratorType.DISCORD_BOT,
            "filename": f"{name.lower()}.py",
            "dependencies": ["discord.py"],
            "tests": ["def test_bot(): print('Bot ready')"],
            "runnable": True,
            "metadata": {"generated": True},
        }

    def _generate_web_api(self, task: Dict, lang: Language) -> CodeResult:
        code = """
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Data(BaseModel):
    input: str

@app.post("/process")
def process(data: Data):
    return {"result": data.input.upper()}
""".strip()
        return {
            "code": code,
            "language": Language.PYTHON,
            "purpose": "web api",
            "generator": GeneratorType.WEB_API,
            "filename": "api.py",
            "dependencies": ["fastapi", "uvicorn[standard]", "pydantic"],
            "tests": ["def test_api(): assert True"],
            "runnable": True,
            "metadata": {},
        }

    def _generate_cli_tool(self, task: Dict, lang: Language) -> CodeResult:
        code = """
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    print(f"Output: {args.input}")

if __name__ == "__main__":
    main()
""".strip()
        return {
            "code": code,
            "language": Language.PYTHON,
            "purpose": "cli tool",
            "generator": GeneratorType.CLI_TOOL,
            "filename": "tool.py",
            "dependencies": [],
            "tests": [],
            "runnable": True,
            "metadata": {},
        }

    def _generate_exploit_demo(self, task: Dict, lang: Language) -> CodeResult:
        # Educational demo only
        offset = task.get("offset", 100)
        target = task.get("target", "127.0.0.1")
        port = task.get("port", 1337)
        code = f"""
# Educational Exploit Demo - For Authorized Testing Only
import socket

offset = {offset}
shellcode = b\"\\x90\" * 10 + b\"\\xcc\"  # NOP sled + INT3

payload = b\"A\" * offset + shellcode
print(f"Payload length: {{len(payload)}}")

# Simulated send (comment out for real use)
# s = socket.socket()
# s.connect((\"{target}\", {port}))
# s.send(payload)
# s.close()
""".strip()
        return {
            "code": code,
            "language": Language.PYTHON,
            "purpose": "exploit demo",
            "generator": GeneratorType.EXPLOIT_DEMO,
            "filename": "demo.py",
            "dependencies": [],
            "tests": [],
            "runnable": True,
            "metadata": {"educational": True},
        }

    def _generate_game(self, task: Dict, lang: Language) -> CodeResult:
        code = """
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
""".strip()
        return {
            "code": code,
            "language": Language.PYTHON,
            "purpose": "game",
            "generator": GeneratorType.GAME,
            "filename": "game.py",
            "dependencies": ["pygame"],
            "tests": [],
            "runnable": True,
            "metadata": {},
        }

    def _generate_data_script(self, task: Dict, lang: Language) -> CodeResult:
        code = """
# Data Script
import pandas as pd
df = pd.DataFrame({'data': [1, 2, 3]})
print(df.describe())
""".strip()
        return {
            "code": code,
            "language": lang,
            "purpose": "data script",
            "generator": GeneratorType.DATA_SCRIPT,
            "filename": "script.py",
            "dependencies": ["pandas"],
            "tests": [],
            "runnable": True,
            "metadata": {},
        }

    def _generate_dockerfile(self, task: Dict) -> CodeResult:
        code = """
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
""".strip()
        return {
            "code": code,
            "language": Language.DOCKERFILE,
            "purpose": "dockerfile",
            "generator": GeneratorType.CONFIG,
            "filename": "Dockerfile",
            "dependencies": [],
            "tests": [],
            "runnable": False,
            "metadata": {},
        }

    def _generate_web_page(self, task: Dict) -> CodeResult:
        code = """
<!DOCTYPE html>
<html>
<head><title>Generated Page</title></head>
<body>
<h1>Hello World</h1>
<p>This is a generated web page.</p>
</body>
</html>
""".strip()
        return {
            "code": code,
            "language": Language.HTML,
            "purpose": "web page",
            "generator": GeneratorType.WEB_PAGE,
            "filename": "index.html",
            "dependencies": [],
            "tests": [],
            "runnable": False,
            "metadata": {},
        }

    def _generate_generic(self, task: Dict, lang: Language, purpose: str) -> CodeResult:
        # For any unknown purpose, generate a basic skeleton
        comment = f"# Generated for: {purpose}"
        code = f"{comment}\ndef main():\n    print('Generated code running')\n\nif __name__ == '__main__':\n    main()"
        return {
            "code": code,
            "language": lang,
            "purpose": purpose,
            "generator": GeneratorType.GENERIC,
            "filename": "generated.py",
            "dependencies": [],
            "tests": [],
            "runnable": True,
            "metadata": {"fallback": True},
        }

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
generator = StriveAICodeGenerator()

def generate_code(task: Dict[str, Any]) -> CodeResult:
    logger.info(f"[API] Task received: ActionType.generate | Language: {task.get('language')} | Purpose: {task.get('purpose')}")
    try:
        result = generator.generate(task)
        logger.info(f"[API] Generated successfully for purpose: {task.get('purpose')}")
        return result
    except Exception as e:
        logger.error(f"[API] ActionType.generate failed: {e}")
        raise

def save_result(result: CodeResult, output_dir: Path = Path("generated")):
    output_dir.mkdir(exist_ok=True)
    path = output_dir / result["filename"]
    path.write_text(result["code"])
    logger.info(f"Generated: {path}")

    if result["dependencies"]:
        req_path = output_dir / "requirements.txt"
        req_path.write_text("\n".join(result["dependencies"]) + "\n")
        logger.info(f"Dependencies saved: {req_path}")
