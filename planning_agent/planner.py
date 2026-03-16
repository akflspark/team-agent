"""작업 분해 및 구현 계획 수립"""

import json

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .llm import LLMClient
from .parser import extract_json
from .prompts import PLAN_SYSTEM, PLAN_USER


def create_plan(client: LLMClient, refined_requirements: dict, console: Console) -> dict:
    """구체화된 요구사항을 기반으로 실행 계획을 생성합니다.

    Returns:
        구현 계획 dict
    """
    console.print()
    console.print(Panel("구현 계획을 수립합니다...", style="cyan"))

    req_text = json.dumps(refined_requirements, ensure_ascii=False, indent=2)

    messages = [
        {
            "role": "user",
            "content": PLAN_USER.format(requirements=req_text),
        }
    ]

    response = client.chat(messages, system=PLAN_SYSTEM)

    try:
        plan = extract_json(response)
        phase_count = len(plan.get("phases", []))
        task_count = sum(len(p.get("tasks", [])) for p in plan.get("phases", []))
        console.print()
        console.print(Markdown(
            f"**{phase_count}개 Phase** | **{task_count}개 태스크** | "
            f"**{len(plan.get('risks', []))}개 리스크** | "
            f"**{len(plan.get('tbd', []))}개 미결 사항**"
        ))
        return plan
    except ValueError:
        console.print("[yellow]JSON 파싱 실패, 기본 구조로 반환합니다.[/yellow]")
        return {"architecture": response, "tech_stack": [], "phases": [],
                "risks": [], "milestones": [], "tbd": []}
