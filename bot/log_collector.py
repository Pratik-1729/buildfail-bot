from __future__ import annotations

import os
from typing import Optional


def read_logs_from_file(file_path: str, tail_lines: Optional[int] = None) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Log file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8", errors="replace") as file_handle:
        if tail_lines is None:
            return file_handle.read()
        # Efficient tail
        lines = file_handle.readlines()
        return "".join(lines[-tail_lines:])


def collect_logs(env: Optional[dict] = None, fallback_text: str = "", tail_lines: int = 150) -> str:
    """
    Collect logs for analysis.

    Priority:
    1. BUILDFAILBOT_LOG_PATH if set
    2. GITHUB_STEP_SUMMARY path if present
    3. Fallback text (may be empty)
    """
    environment = env or os.environ

    log_path = environment.get("BUILDFAILBOT_LOG_PATH")
    if log_path:
        try:
            return read_logs_from_file(log_path, tail_lines)
        except (FileNotFoundError, OSError):
            pass

    step_summary_path = environment.get("GITHUB_STEP_SUMMARY")
    if step_summary_path and os.path.exists(step_summary_path):
        try:
            return read_logs_from_file(step_summary_path, tail_lines)
        except (FileNotFoundError, OSError):
            pass

    return fallback_text or ""