"""LLM 응답에서 JSON을 추출하는 유틸리티"""

import json
import re


def extract_json(text: str) -> dict:
    """LLM 응답 텍스트에서 JSON 객체를 추출합니다.

    ```json ... ``` 코드블록 안의 JSON을 우선 파싱하고,
    없으면 텍스트 전체에서 첫 번째 { ... } 블록을 파싱합니다.
    """
    # 1) ```json ... ``` 블록 추출
    match = re.search(r"```json\s*([\s\S]*?)```", text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 2) ``` ... ``` 블록 (json 태그 없이)
    match = re.search(r"```\s*([\s\S]*?)```", text)
    if match:
        candidate = match.group(1).strip()
        if candidate.startswith("{"):
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

    # 3) 텍스트에서 가장 바깥쪽 { ... } 추출
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    start = -1

    raise ValueError("LLM 응답에서 JSON을 추출할 수 없습니다.")
