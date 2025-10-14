from __future__ import annotations

import os
from typing import Optional, List

import requests

from .classifier import Classification  # For type hinting


class GitHubCommenter:
    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token or os.environ.get("GITHUB_TOKEN")

    def comment_on_pr(self, repository: str, pull_number: int, body: str, dry_run: bool = False) -> None:
        if dry_run or not self.token:
            print("[DRY-RUN] Would post comment to PR #{} in {}:\n{}".format(pull_number, repository, body))
            return

        url = f"https://api.github.com/repos/{repository}/issues/{pull_number}/comments"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }
        response = requests.post(url, headers=headers, json={"body": body}, timeout=30)
        if response.status_code >= 300:
            raise RuntimeError(f"Failed to post comment: {response.status_code} {response.text}")

    @staticmethod
    def format_classifications(classifications: List[Classification]) -> str:
        if not classifications:
            return "No failure patterns detected."
        lines = ["### Build Failure Analysis:"]
        for c in classifications:
            lines.append(f"- **Category:** `{c.category}` (confidence: {c.confidence:.2f})")
            if c.matches:
                lines.append(f"  - Matches: {', '.join(c.matches)}")
        return "\n".join(lines)