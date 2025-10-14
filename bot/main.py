from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from .classifier import FailureClassifier
from .commenter import GitHubCommenter
from .log_collector import collect_logs
from .suggestion_generator import SuggestionGenerator


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BuildFailBot CLI")
    parser.add_argument("--dry-run", action="store_true", help="Print output instead of posting to GitHub")
    parser.add_argument("--tail-lines", type=int, default=150, help="Tail last N log lines")
    parser.add_argument("--log-path", type=str, default=None, help="Explicit path to a log file to read")
    parser.add_argument("--category", type=str, default=None, help="Force category (for debugging)")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    # Collect logs
    fallback_text = ""
    env = dict(os.environ)
    if args.log_path:
        env["BUILDFAILBOT_LOG_PATH"] = args.log_path
    logs = collect_logs(env=env, fallback_text=fallback_text, tail_lines=args.tail_lines)

    # Classify (now returns a list)
    classifier = FailureClassifier()
    if args.category:
        # Forced category for debugging
        classifications = [
            type("Classification", (), {
                "category": args.category,
                "matches": [],
                "confidence": 0.5
            })()
        ]
    else:
        classifications = classifier.classify(logs)

    # Generate suggestion body for each classification
    sugg = SuggestionGenerator()
    suggestion_bodies = [
        sugg.render(category=c.category, matches=c.matches, confidence=c.confidence)
        for c in classifications
    ]
    # Combine all suggestions into one body
    body = "\n\n---\n\n".join(suggestion_bodies)

    # Optionally, also show a summary table using the commenter formatter
    summary = GitHubCommenter.format_classifications(classifications)
    body = summary + "\n\n" + body

    # Determine PR context from env (GitHub Actions)
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    pr_number_str = os.environ.get("PR_NUMBER")
    try:
        pull_number = int(pr_number_str) if pr_number_str else 0
    except ValueError:
        pull_number = 0

    # Comment (or dry-run print)
    commenter = GitHubCommenter()
    if repository and pull_number > 0:
        commenter.comment_on_pr(repository=repository, pull_number=pull_number, body=body, dry_run=args.dry_run)
    else:
        print(body)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


