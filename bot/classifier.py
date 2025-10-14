from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Classification:
    category: str
    confidence: float
    matches: List[str]


class FailureClassifier:
    def __init__(self, category_to_patterns: Optional[Dict[str, List[str]]] = None) -> None:
        self.category_to_patterns: Dict[str, List[re.Pattern]] = {}
        patterns = category_to_patterns or self._default_patterns()
        for category, pattern_list in patterns.items():
            self.category_to_patterns[category] = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in pattern_list]

    def classify(self, logs: str) -> List[Classification]:
        results: List[Classification] = []

        for category, regexes in self.category_to_patterns.items():
            matches: List[str] = []
            for regex in regexes:
                for match in regex.findall(logs):
                    if isinstance(match, tuple):
                        matches.append(" ".join([m for m in match if m]))
                    else:
                        matches.append(str(match))
            if matches:
                confidence = min(1.0, 0.2 + 0.2 * len(matches))
                results.append(Classification(category=category, confidence=confidence, matches=matches))

        if not results:
            results.append(Classification(category="unknown", confidence=0.1, matches=[]))

        # Sort by confidence descending
        results.sort(key=lambda c: c.confidence, reverse=True)
        return results

    @staticmethod
    def _default_patterns() -> Dict[str, List[str]]:
        return {
            "test-failure": [
                r"AssertionError",
                r"FAILED\s+tests?",
                r"\bpytest\b.*failed",
            ],
            "dependency-error": [
                r"ModuleNotFoundError: No module named",
                r"ImportError: cannot import name",
                r"pip\s+install\s+failed",
            ],
            "lint-error": [
                r"flake8|ruff\b.*error",
                r"ESLint|pylint\b.*(error|fatal)",
            ],
            "build-error": [
                r"error: command '.*' failed",
                r"CMake Error|make: \*\*\*",
                r"fatal error:.*No such file or directory",
            ],
            "timeout": [
                r"Timeout\b|timed out",
                r"job exceeded the maximum time",
            ],
        }