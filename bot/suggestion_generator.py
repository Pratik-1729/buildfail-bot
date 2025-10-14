from __future__ import annotations

import os
from typing import Dict, List, Optional

import yaml


class SuggestionGenerator:
    def __init__(self, suggestions_path: Optional[str] = None) -> None:
        default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "suggestions.yaml")
        self.suggestions_path = suggestions_path or default_path
        self._data: Dict[str, Dict[str, List[str]]] = self._load_yaml()

    def _load_yaml(self) -> Dict[str, Dict[str, List[str]]]:
        if not os.path.exists(self.suggestions_path):
            return {}
        with open(self.suggestions_path, "r", encoding="utf-8") as file_handle:
            raw = yaml.safe_load(file_handle) or {}
        # Normalize structure
        data: Dict[str, Dict[str, List[str]]] = {}
        for category, section in raw.items():
            tips = section.get("tips", []) if isinstance(section, dict) else []
            title = section.get("title", category) if isinstance(section, dict) else category
            data[category] = {"title": [str(title)], "tips": [str(t) for t in tips]}
        return data

    def render(self, category: str, matches: Optional[List[str]] = None, confidence: Optional[float] = None) -> str:
        section = self._data.get(category) or self._data.get("unknown") or {"title": [category], "tips": []}
        title = section.get("title", [category])[0]
        tips = section.get("tips", [])
        matches_info = "\n".join([f"- matched: {m}" for m in (matches or [])])
        tips_lines = "\n".join([f"- {tip}" for tip in tips])
        conf_line = f"Confidence: {round(confidence * 100)}%\n\n" if confidence is not None else ""
        body = (
            f"## {title}\n\n"
            + conf_line
            + ("### Evidence\n" + matches_info + "\n\n" if matches_info else "")
            + ("### Next steps\n" + tips_lines if tips_lines else "")
        )
        return body 