"""File storage implementation."""

from pathlib import Path
from typing import Optional
import shutil


class FileStorage:
    """Local file storage implementation."""

    def __init__(self, base_path: Path = Path("./uploads")):
        self._base_path = base_path
        self._base_path.mkdir(parents=True, exist_ok=True)

    def store(self, source_path: Path, document_id: str) -> Path:
        """Store a file.

        Args:
            source_path: Path to the source file
            document_id: Document ID to use as filename

        Returns:
            Path to the stored file
        """
        destination = self._base_path / f"{document_id}.docx"
        shutil.copy2(source_path, destination)
        return destination

    def retrieve(self, document_id: str) -> Optional[Path]:
        """Retrieve a file by document ID.

        Args:
            document_id: Document ID

        Returns:
            Path to the file, or None if not found
        """
        file_path = self._base_path / f"{document_id}.docx"
        return file_path if file_path.exists() else None

    def delete(self, document_id: str) -> bool:
        """Delete a file by document ID.

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        file_path = self._base_path / f"{document_id}.docx"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def exists(self, document_id: str) -> bool:
        """Check if a file exists."""
        file_path = self._base_path / f"{document_id}.docx"
        return file_path.exists()