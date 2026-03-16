"""Claude/OpenAI 통합 LLM 클라이언트"""

import sys

from rich.console import Console

console = Console(stderr=True)


class LLMClient:
    """두 LLM 프로바이더를 하나의 chat() 인터페이스로 통합합니다."""

    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider
        self.model = model

        if provider == "claude":
            import anthropic

            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            import openai

            self.client = openai.OpenAI(api_key=api_key)

    def chat(self, messages: list[dict], system: str = "") -> str:
        """메시지를 보내고 응답 텍스트를 반환합니다.

        Args:
            messages: [{"role": "user"|"assistant", "content": str}, ...]
            system: 시스템 프롬프트 (선택)

        Returns:
            어시스턴트의 응답 텍스트
        """
        try:
            if self.provider == "claude":
                return self._chat_claude(messages, system)
            else:
                return self._chat_openai(messages, system)
        except Exception as e:
            console.print(f"[bold red]API 오류:[/bold red] {e}")
            sys.exit(1)

    def _chat_claude(self, messages: list[dict], system: str) -> str:
        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def _chat_openai(self, messages: list[dict], system: str) -> str:
        oai_messages = []
        if system:
            oai_messages.append({"role": "system", "content": system})
        oai_messages.extend(messages)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=oai_messages,
            max_tokens=4096,
        )
        return response.choices[0].message.content
