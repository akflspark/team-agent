"""요구사항 구체화 - 대화형 질문을 통해 모호한 요구사항을 정제합니다."""

import json

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .llm import LLMClient
from .parser import extract_json
from .prompts import REFINE_FINALIZE, REFINE_INITIAL_USER, REFINE_SYSTEM


def refine_requirements(client: LLMClient, raw_input: str, console: Console) -> dict:
    """대화형 루프를 통해 요구사항을 구체화합니다.

    Returns:
        구체화된 요구사항 dict
    """
    messages = []

    messages.append({
        "role": "user",
        "content": REFINE_INITIAL_USER.format(requirement=raw_input),
    })

    console.print()
    console.print(Panel("요구사항을 분석하고 질문을 준비합니다...", style="cyan"))

    response = client.chat(messages, system=REFINE_SYSTEM)
    messages.append({"role": "assistant", "content": response})

    console.print()
    console.print(Markdown(response))
    console.print()

    round_num = 1
    while True:
        console.print(
            f"[bold green]━━━ 라운드 {round_num} ━━━[/bold green]"
        )
        console.print(
            "[dim]답변을 입력하세요. 'done'을 입력하면 요구사항을 최종 정리합니다.[/dim]"
        )

        try:
            user_input = console.input("[bold yellow]> [/bold yellow]").strip()
        except (EOFError, KeyboardInterrupt):
            user_input = "done"
            console.print()

        if not user_input:
            continue

        if user_input.lower() == "done":
            console.print()
            console.print(Panel("요구사항을 최종 정리합니다...", style="cyan"))
            messages.append({"role": "user", "content": REFINE_FINALIZE})
            final_response = client.chat(messages, system=REFINE_SYSTEM)

            try:
                result = extract_json(final_response)
                console.print()
                console.print(Markdown(
                    f"**프로젝트:** {result.get('project_name', '')}\n\n"
                    f"{result.get('summary', '')}\n\n"
                    f"**필수 기능:** {len(result.get('features_must', []))}개 | "
                    f"**선택 기능:** {len(result.get('features_nice', []))}개"
                ))
                return result
            except ValueError:
                console.print("[yellow]JSON 파싱 실패, 원본 텍스트를 반환합니다.[/yellow]")
                return {"project_name": "프로젝트", "summary": final_response,
                        "goals": [], "target_users": "", "features_must": [],
                        "features_nice": [], "non_functional": [], "tech_stack": [],
                        "constraints": []}

        messages.append({"role": "user", "content": user_input})
        console.print()
        console.print(Panel("답변을 분석하고 후속 질문을 준비합니다...", style="cyan"))

        response = client.chat(messages, system=REFINE_SYSTEM)
        messages.append({"role": "assistant", "content": response})

        console.print()
        console.print(Markdown(response))
        console.print()

        round_num += 1
