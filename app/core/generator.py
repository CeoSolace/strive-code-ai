# generator.py
"""
STRIVE CODE AI – UNIVERSAL CODE GENERATOR (FREE LOCAL LLM + FULL STACK)
=====================================================================
- 100% offline after model download
- FastAPI web API + CLI mode
- Uses Qwen2-7B-Instruct (4-bit) or any HF model
- Generates: APIs, CLI tools, games, exploits (demo), data scripts, web pages, etc.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional

import torch
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
from jinja2 import Template

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("STRIVE_CODE_AI")

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
MODEL_ID = "Qwen/Qwen2-7B-Instruct"  # Change to any code model
USE_4BIT = True
MAX_NEW_TOKENS = 1024
TEMPERATURE = 0.3

# --------------------------------------------------------------------------- #
# Enums
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

class GeneratorType(str, Enum):
    WEB_API = "web_api"
    CLI_TOOL = "cli_tool"
    DISCORD_BOT = "discord_bot"
    EXPLOIT_DEMO = "exploit_demo"
    GAME = "game"
    DATA_SCRIPT = "data_script"
    WEB_PAGE = "web_page"
    GENERIC = "generic"

# --------------------------------------------------------------------------- #
# LLM Loader (Free & Local)
# --------------------------------------------------------------------------- #
class LocalLLM:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        logger.info(f"Loading model: {MODEL_ID}")
        quantization_config = None
        if USE_4BIT:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            quantization_config=quantization_config,
            trust_remote_code=True,
        )
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            do_sample=True,
            top_p=0.9,
        )
        logger.info("LLM loaded successfully.")

    def generate(self, prompt: str) -> str:
        outputs = self.pipe(prompt)
        return outputs[0]["generated_text"].split("```")[-1].strip("` \n")

llm = LocalLLM()

# --------------------------------------------------------------------------- #
# Code Result
# --------------------------------------------------------------------------- #
@dataclass
class CodeResult:
    code: str
    language: Language
    purpose: str
    generator: GeneratorType
    filename: str
    dependencies: List[str] = field(default_factory=list)
    tests: List[str] = field(default_factory=list)
    runnable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

# --------------------------------------------------------------------------- #
# Universal Generator
# --------------------------------------------------------------------------- #
class StriveAICodeGenerator:
    def generate(self, task: Dict[str, Any]) -> CodeResult:
        purpose = task.get("purpose", "").lower()
        language = Language(task.get("language", "python").lower())

        # Route by purpose
        if "discord" in purpose and "bot" in purpose:
            return self._discord_bot(task, language)
        elif "api" in purpose or "web" in purpose or "fastapi" in purpose:
            return self._web_api(task, language)
        elif "cli" in purpose or "tool" in purpose or "command" in purpose:
            return self._cli_tool(task, language)
        elif "exploit" in purpose or "payload" in purpose:
            return self._exploit_demo(task, language)
        elif "game" in purpose:
            return self._game(task, language)
        elif "data" in purpose or "script" in purpose or "pandas" in purpose:
            return self._data_script(task, language)
        elif "docker" in purpose:
            return self._dockerfile(task)
        elif "html" in purpose or "page" in purpose:
            return self._web_page(task)
        else:
            return self._ai_generate(task, language, purpose)

    def _ai_generate(self, task: Dict, lang: Language, purpose: str) -> CodeResult:
        prompt = f"""
You are an expert programmer. Generate **complete, runnable, well-commented code** in **{lang.value}** for:

> {purpose}

Requirements:
- Include all necessary imports
- Add a main function or entrypoint
- Save output if needed
- Be safe and educational
- Return ONLY the code block (no explanation)

```python
"""
        code = llm.generate(prompt)
        return CodeResult(
            code=code,
            language=lang,
            purpose=purpose,
            generator=GeneratorType.GENERIC,
            filename=f"generated_{purpose.replace(' ', '_')}.py",
            dependencies=[],
            runnable=True,
        )

    def _discord_bot(self, task: Dict, lang: Language) -> CodeResult:
        name = task.get("name", "MyBot")
        prefix = task.get("prefix", "!")
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
async def hello(ctx):
    await ctx.send('Hello from {name}!')

bot.run(os.getenv('DISCORD_TOKEN'))
"""
        return CodeResult(
            code=code.strip(),
            language=Language.PYTHON,
            purpose="Discord Bot",
            generator=GeneratorType.DISCORD_BOT,
            filename="bot.py",
            dependencies=["discord.py"],
            runnable=True,
        )

    def _web_api(self, task: Dict, lang: Language) -> CodeResult:
        code = """
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Generated API")

class Input(BaseModel):
    data: str

@app.post("/process")
def process(input: Input):
    return {"result": input.data.upper()}

@app.get("/")
def home():
    return {"message": "API is running!"}
"""
        return CodeResult(
            code=code.strip(),
            language=Language.PYTHON,
            purpose="Web API",
            generator=GeneratorType.WEB_API,
            filename="main.py",
            dependencies=["fastapi", "uvicorn", "pydantic"],
            runnable=True,
        )

    def _cli_tool(self, task: Dict, lang: Language) -> CodeResult:
        code = """
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generated CLI Tool")
    parser.add_argument("--input", required=True, help="Input string")
    args = parser.parse_args()
    print(f"Processed: {{args.input[::-1]}}")

if __name__ == "__main__":
    main()
"""
        return CodeResult(
            code=code.strip(),
            language=Language.PYTHON,
            purpose="CLI Tool",
            generator=GeneratorType.CLI_TOOL,
            filename="tool.py",
            dependencies=[],
            runnable=True,
        )

    def _exploit_demo(self, task: Dict, lang: Language) -> CodeResult:
        code = '''
# EDUCATIONAL DEMO ONLY - DO NOT USE MALICIOUSLY
import socket

def demo_payload():
    offset = 100
    shellcode = b"\\x90" * 16 + b"\\xcc"  # NOP + INT3
    payload = b"A" * offset + shellcode
    print(f"Payload length: {{len(payload)}}")
    # s = socket.socket()
    # s.connect(("127.0.0.1", 1337))
    # s.send(payload)
    # s.close()

if __name__ == "__main__":
    demo_payload()
'''
        return CodeResult(
            code=code.strip(),
            language=Language.PYTHON,
            purpose="Exploit Demo (Educational)",
            generator=GeneratorType.EXPLOIT_DEMO,
            filename="demo_exploit.py",
            dependencies=[],
            runnable=True,
            metadata={"educational": True},
        )

    def _game(self, task: Dict, lang: Language) -> CodeResult:
        code = '''
import pygame
import random

pygame.init()
screen = pygame.display.set_mode((600, 400))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 55)

x = 300
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: x -= 5
    if keys[pygame.K_RIGHT]: x += 5
    screen.fill((0, 0, 50))
    pygame.draw.circle(screen, (255, 100, 100), (x, 200), 40)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
'''
        return CodeResult(
            code=code.strip(),
            language=Language.PYTHON,
            purpose="Simple Game",
            generator=GeneratorType.GAME,
            filename="game.py",
            dependencies=["pygame"],
            runnable=True,
        )

    def _data_script(self, task: Dict, lang: Language) -> CodeResult:
        code = '''
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'A': np.random.randn(100),
    'B': np.random.choice(['X', 'Y', 'Z'], 100)
})
print(df.describe(include='all'))
df.to_csv('output.csv', index=False)
'''
        return CodeResult(
            code=code.strip(),
            language=Language.PYTHON,
            purpose="Data Analysis Script",
            generator=GeneratorType.DATA_SCRIPT,
            filename="analyze.py",
            dependencies=["pandas", "numpy"],
            runnable=True,
        )

    def _dockerfile(self, task: Dict) -> CodeResult:
        code = '''
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "main.py"]
'''
        return CodeResult(
            code=code.strip(),
            language=Language.DOCKERFILE,
            purpose="Dockerfile",
            generator=GeneratorType.CONFIG,
            filename="Dockerfile",
            dependencies=[],
            runnable=False,
        )

    def _web_page(self, task: Dict) -> CodeResult:
        code = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Generated Page</title>
    <style>body { font-family: Arial; padding: 2rem; }</style>
</head>
<body>
    <h1>Hello from AI!</h1>
    <p>This page was auto-generated.</p>
    <script>console.log("Loaded!");</script>
</body>
</html>
'''
        return CodeResult(
            code=code.strip(),
            language=Language.HTML,
            purpose="Web Page",
            generator=GeneratorType.WEB_PAGE,
            filename="index.html",
            dependencies=[],
            runnable=False,
        )

# --------------------------------------------------------------------------- #
# FastAPI App
# --------------------------------------------------------------------------- #
app = FastAPI(title="Strive Code AI Generator", version="1.0")

class GenerateRequest(BaseModel):
    purpose: str
    language: str = "python"
    name: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

generator = StriveAICodeGenerator()

@app.post("/generate")
def generate_code(req: GenerateRequest):
    task = req.dict()
    try:
        result = generator.generate(task)
        save_result(result)
        return result
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
def download_file(filename: str):
    path = Path("generated") / filename
    if path.exists():
        return FileResponse(path)
    raise HTTPException(404, "File not found")

# --------------------------------------------------------------------------- #
# Save Helper
# --------------------------------------------------------------------------- #
def save_result(result: CodeResult, output_dir: Path = Path("generated")):
    output_dir.mkdir(exist_ok=True)
    path = output_dir / result.filename
    path.write_text(result.code)
    logger.info(f"Saved: {path}")

    if result.dependencies:
        req_path = output_dir / "requirements.txt"
        req_path.write_text("\n".join(result.dependencies) + "\n")
        logger.info(f"Dependencies: {req_path}")

# --------------------------------------------------------------------------- #
# CLI Mode
# --------------------------------------------------------------------------- #
def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--purpose", required=True, help="What to generate")
    parser.add_argument("--language", default="python")
    parser.add_argument("--serve", action="store_true", help="Run web server")
    args = parser.parse_args()

    if args.serve:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        task = {"purpose": args.purpose, "language": args.language}
        result = generator.generate(task)
        save_result(result)
        print(f"\nGenerated: {result.filename}\n")
        print(result.code)

if __name__ == "__main__":
    cli()
