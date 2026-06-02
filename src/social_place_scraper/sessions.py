from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class ManagedSession:
    name: str
    root: Path
    profile_dir: Path
    cookie_file: Path
    metadata_file: Path


class SessionManager:
    def __init__(self, root: Path):
        self.root = root

    def get(self, name: str) -> ManagedSession:
        safe_name = self._safe_name(name)
        session_root = self.root / safe_name
        session = ManagedSession(
            name=safe_name,
            root=session_root,
            profile_dir=session_root / "browser-profile",
            cookie_file=session_root / "cookies.json",
            metadata_file=session_root / "metadata.json",
        )
        session.profile_dir.mkdir(parents=True, exist_ok=True)
        self._touch_metadata(session)
        return session

    def _safe_name(self, name: str) -> str:
        safe_name = "".join(char if char.isalnum() or char in "-_" else "_" for char in name.strip())
        if not safe_name or not any(char.isalnum() for char in safe_name):
            raise ValueError("Session name must include at least one letter or number.")
        return safe_name

    def _touch_metadata(self, session: ManagedSession) -> None:
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "name": session.name,
            "profileDir": str(session.profile_dir),
            "cookieFile": str(session.cookie_file),
            "lastUsedAt": now,
        }
        session.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        session.metadata_file.write_text(json.dumps(payload, indent=2) + "\n")
