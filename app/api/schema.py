# app/api/schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import re

class ActionType(str, Enum):
    generate = "generate"
    transpile = "transpile"
    reconstruct = "reconstruct"
    debug = "debug"
    optimize = "optimize"
    explain = "explain"
    learn = "learn"
    diagram = "diagram"
    pdf = "pdf"
    voice = "voice"
    upgrade = "upgrade"
    unrestricted = "unrestricted"

class CodeTask(BaseModel):
    action: ActionType = Field(..., description="Core AI operation to perform")
    code: Optional[str] = Field(None, description="Source code input (for debug, optimize, transpile, etc.)")
    language: Optional[str] = Field("python", description="Target or source programming language")
    purpose: Optional[str] = Field(None, description="High-level intent for generation (e.g., 'REST API with auth')")
    github_url: Optional[str] = Field(None, description="Public GitHub repo URL for reconstruction")
    modifications: Optional[List[str]] = Field(default_factory=list, description="Changes to apply during reconstruction")
    constraints: Optional[List[str]] = Field(default_factory=list, description="Performance, security, or style constraints")
    output_format: Optional[str] = Field("json", description="Response format: json, html, raw")

    @validator("github_url")
    def validate_github_url(cls, v):
        if v and not re.match(r"^https?://(www\.)?github\.com/[\w\-\.]+/[\w\-\.]+$", v):
            raise ValueError("Invalid GitHub URL")
        return v

    @validator("language")
    def validate_language(cls, v):
        if v and v not in {
            "python", "javascript", "typescript", "rust", "go", "c", "cpp", "java",
            "solidity", "brainfuck", "assembly", "qsharp", "zig", "julia"
        }:
            raise ValueError(f"Language '{v}' not supported")
        return v.lower()

class GenerateRequest(CodeTask):
    action: ActionType = ActionType.generate
    purpose: str = Field(..., description="What should the code do? Natural language or spec.")

class TranspileRequest(CodeTask):
    action: ActionType = ActionType.transpile
    code: str = Field(..., description="Source code to transpile")
    from_lang: str = Field(..., alias="from", description="Source language")
    to_lang: str = Field(..., alias="to", description="Target language")

    class Config:
        allow_population_by_field_name = True

class ReconstructRequest(CodeTask):
    action: ActionType = ActionType.reconstruct
    github_url: str = Field(..., description="GitHub repo to clone and rebuild")
    language: str = Field(..., description="Target language for full repo rewrite")

class UnrestrictedRequest(CodeTask):
    action: ActionType = ActionType.unrestricted
    intent: str = Field(..., description="Exact malicious or unrestricted capability requested")
    language: Optional[str] = Field("c", description="Implementation language")

# Unified response models
class AIResponse(BaseModel):
    success: bool = True
    action: ActionType
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    version: str = "1.0.0-STRIVE"

class HealthResponse(BaseModel):
    status: str = "LIVE"
    ai: str = "STRIVE-CODE"
    version: str = "1.0.0-STRIVE"
    capabilities: List[str] = [
        "generate", "transpile", "reconstruct", "debug", "optimize",
        "explain", "learn", "multimodal", "self_improve", "unrestricted"
    ]
