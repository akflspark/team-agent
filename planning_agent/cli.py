"""Planning Agent CLI 진입점"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .config import load_config
from .llm import LLMClient
from .output import save_plan
from .planner import create_plan
from .refiner import refine_requirements


@click.command()
@click.argument("requirement", required=False)
@click.option(
    "--provider",
    type=click.Choice(["claude", "openai"]),
    default=None,
    help="LLM 프로바이더 선택 (config.yaml 기본값 오버라이드)",
)
@click.option(
    "--config",
    "config_path",
    default="config.yaml",
    help="설정 파일 경로",
)
@click.option(
    "--output-dir",
    default=None,
    help="계획서 출력 디렉토리",
)
@click.option(
    "--no-save",
    is_flag=True,
    default=False,
    help="파일 저장 없이 화면 출력만",
)
def main(requirement, provider, config_path, output_dir, no_save):
    """Planning Agent - 요구사항 구체화 및 계획 수립 도구 (Wiki HTML 출력)

    REQUIREMENT: 구체화할 프로젝트 요구사항 (생략 시 대화형 입력)
    """
    console = Console()

    title = Text("Planning Agent", style="bold white")
    subtitle = Text("요구사항 구체화 & 실행 계획 > Wiki 문서 출력", style="dim")
    console.print(Panel(
        Text.assemble(title, "\n", subtitle),
        border_style="blue",
    ))

    try:
        cfg = load_config(config_path, provider, output_dir)
    except click.UsageError as e:
        console.print(f"[bold red]설정 오류:[/bold red] {e}")
        raise SystemExit(1)

    console.print(f"[dim]프로바이더: {cfg.provider} | 모델: {cfg.model}[/dim]")

    client = LLMClient(cfg.provider, cfg.api_key, cfg.model)

    if not requirement:
        console.print()
        console.print("[bold]구체화할 프로젝트 요구사항을 입력하세요:[/bold]")
        try:
            requirement = console.input("[bold yellow]> [/bold yellow]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]종료합니다.[/dim]")
            return

        if not requirement:
            console.print("[red]요구사항이 입력되지 않았습니다.[/red]")
            return

    # Phase 1: 요구사항 구체화 (dict 반환)
    console.print()
    console.print(Panel("Phase 1: 요구사항 구체화", style="bold green"))
    refined = refine_requirements(client, requirement, console)

    # Phase 2: 구현 계획 수립 (dict 반환)
    console.print()
    console.print(Panel("Phase 2: 구현 계획 수립", style="bold green"))
    plan = create_plan(client, refined, console)

    # 위키 HTML 저장
    if not no_save:
        filepath = save_plan(refined, plan, cfg.output_dir)
        console.print()
        console.print(Panel(
            f"[bold green]계획서가 저장되었습니다[/bold green]\n{filepath}",
            border_style="green",
        ))
    else:
        console.print()
        console.print("[dim]--no-save 옵션으로 파일 저장을 건너뛰었습니다.[/dim]")

    console.print()
    console.print("[bold]완료![/bold]")


if __name__ == "__main__":
    main()
