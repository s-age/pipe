"""Service that encapsulates session-file searching logic.

This keeps filesystem traversal and matching logic in a testable place
separate from the web action layer.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable


class SearchSessionsService:
    """Search sessions under a sessions directory.

    The service exposes a single `search(query)` method which returns a list
    of dicts with `session_id` and `title` keys.
    """

    def __init__(self, sessions_dir: str):
        self.sessions_dir = sessions_dir

    def _iter_session_files(self) -> Iterable[str]:
        for root, _, files in os.walk(self.sessions_dir):
            # Skip backups directory
            if "backups" in root.split(os.path.sep):
                continue
            for fname in files:
                if not fname.lower().endswith(".json"):
                    continue
                yield os.path.join(root, fname)

    def _compute_session_id(self, fpath: str) -> str:
        rel = os.path.relpath(fpath, self.sessions_dir)
        if rel.endswith(".json"):
            session_id = rel[:-5]
            # Normalize separators to '/'
            return session_id.replace(os.path.sep, "/")
        return rel

    def search(self, query: str) -> list[dict[str, str]]:
        """Return matching sessions for `query`.

        Matching rules:
        - If query is found in filename (case-insensitive) -> match.
        - Otherwise, try to load JSON and match against `purpose`,
          `background`, or turns' `instruction`/`content` fields.
        Sessions are returned only once even if multiple turns match.
        """
        q = (query or "").strip()
        if not q:
            return []

        qlow = q.lower()
        matches: dict[str, dict[str, str]] = {}

        for fpath in self._iter_session_files():
            fname = os.path.basename(fpath)
            session_id = self._compute_session_id(fpath)
            title = None
            matched = False

            # Skip if already matched
            if session_id in matches:
                continue

            # 1. Filename match
            if qlow in fname.lower():
                title = os.path.splitext(fname)[0]
                matched = True
            else:
                # 2. JSON fields match
                try:
                    with open(fpath, encoding="utf-8") as fh:
                        data = json.load(fh)
                except Exception:
                    continue

                purpose = data.get("purpose") or ""
                background = data.get("background") or ""
                if qlow in purpose.lower():
                    title = purpose
                    matched = True
                elif qlow in background.lower():
                    title = purpose or background
                    matched = True
                else:
                    # 3. turns (instruction/content) match
                    turns = data.get("turns") or []
                    for t in turns:
                        if not isinstance(t, dict):
                            continue
                        instr = t.get("instruction")
                        content = t.get("content")
                        if instr and qlow in str(instr).lower():
                            title = purpose or background or os.path.splitext(fname)[0]
                            matched = True
                            break
                        if content and qlow in str(content).lower():
                            title = purpose or background or os.path.splitext(fname)[0]
                            matched = True
                            break

            if matched:
                matches[session_id] = {
                    "session_id": session_id,
                    "title": title or os.path.splitext(fname)[0],
                }

        return list(matches.values())
