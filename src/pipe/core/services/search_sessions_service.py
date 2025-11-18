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

        Matching rules (kept intentionally simple and compatible with the
        previous action implementation):
        - If query is found in filename (case-insensitive) -> match.
        - Otherwise, try to load JSON and match against `purpose` or
          `background` fields.
        """
        q = (query or "").strip()
        if not q:
            return []

        qlow = q.lower()
        matches: list[dict[str, str]] = []

        for fpath in self._iter_session_files():
            fname = os.path.basename(fpath)
            if qlow in fname.lower():
                title = os.path.splitext(fname)[0]  # Default title from filename
                matches.append(
                    {"session_id": self._compute_session_id(fpath), "title": title}
                )
                continue

            try:
                with open(fpath, encoding="utf-8") as fh:
                    data = json.load(fh)
            except Exception:
                continue

            purpose = data.get("purpose") or ""
            # background = (data.get("background") or "") # Unused variable, removed
            found = False
            title = purpose or os.path.splitext(fname)[0]  # Define title before use
            matches.append(
                {"session_id": self._compute_session_id(fpath), "title": title}
            )

            # Also search within turns (instruction/content) to support matching
            # cases where the query appears in conversation text rather than meta.
            if not found:
                turns = data.get("turns") or []
                for t in turns:
                    instr = t.get("instruction") if isinstance(t, dict) else None
                    content = t.get("content") if isinstance(t, dict) else None
                    if instr and qlow in str(instr).lower():
                        title = purpose or os.path.splitext(fname)[0]
                        matches.append(
                            {
                                "session_id": self._compute_session_id(fpath),
                                "title": title,
                            }
                        )
                        found = True
                        break
                    if content and qlow in str(content).lower():
                        title = purpose or os.path.splitext(fname)[0]
                        matches.append(
                            {
                                "session_id": self._compute_session_id(fpath),
                                "title": title,
                            }
                        )
                        found = True
                        break

        return matches
