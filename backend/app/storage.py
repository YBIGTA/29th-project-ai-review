from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile


class LocalStorage:
    """Stores uploaded files below a local directory using generated IDs."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.audio_dir = self.root / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    async def save_audio(self, upload: UploadFile) -> tuple[str, str]:
        review_id = uuid.uuid4().hex
        suffix = Path(upload.filename or "audio").suffix.lower()
        filename = f"{review_id}{suffix}"
        path = self.audio_dir / filename
        await self._save_upload(upload, path)
        return review_id, filename

    def audio_path(self, filename: str) -> Path:
        return self.audio_dir / filename

    @staticmethod
    async def _save_upload(upload: UploadFile, destination: Path) -> None:
        try:
            with destination.open("wb") as output:
                while chunk := await upload.read(1024 * 1024):
                    output.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
