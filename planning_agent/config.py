"""설정 로딩 - YAML 파일 + 환경변수 지원"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import click
import yaml


@dataclass
class Config:
    provider: str
    api_key: str
    model: str
    output_dir: str


def load_config(
    config_path: str = "config.yaml",
    provider_override: Optional[str] = None,
    output_dir_override: Optional[str] = None,
) -> Config:
    """설정 파일과 환경변수에서 설정을 로드합니다."""
    cfg = {}
    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file, encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

    provider = provider_override or cfg.get("provider", "claude")

    # API 키: 환경변수 우선, YAML 파일 폴백
    if provider == "claude":
        api_key = (
            os.environ.get("ANTHROPIC_API_KEY")
            or cfg.get("anthropic_api_key")
            or ""
        )
        model = cfg.get("claude_model", "claude-sonnet-4-20250514")
    else:
        api_key = (
            os.environ.get("OPENAI_API_KEY")
            or cfg.get("openai_api_key")
            or ""
        )
        model = cfg.get("openai_model", "gpt-4o")

    if not api_key:
        env_var = "ANTHROPIC_API_KEY" if provider == "claude" else "OPENAI_API_KEY"
        raise click.UsageError(
            f"API 키가 설정되지 않았습니다. "
            f"config.yaml에 설정하거나 환경변수 {env_var}를 설정하세요."
        )

    output_dir = output_dir_override or cfg.get("output_dir", "./plans")

    return Config(
        provider=provider,
        api_key=api_key,
        model=model,
        output_dir=output_dir,
    )
