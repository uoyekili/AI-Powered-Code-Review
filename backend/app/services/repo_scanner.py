import logging
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from app.config.settings import get_settings
from app.utils.file_utils import (
    LANGUAGE_MAP,
    METADATA_FILES,
    count_lines,
    is_source_file,
    should_ignore_path,
)

logger = logging.getLogger(__name__)


@dataclass
class ScannedFile:
    path: str
    name: str
    extension: str
    lines: int
    content: str
    priority: int = 0


@dataclass
class ScanResult:
    files: list[ScannedFile] = field(default_factory=list)
    metadata_content: dict[str, str] = field(default_factory=dict)
    languages: list[str] = field(default_factory=list)
    primary_language: str = "Unknown"
    file_count: int = 0
    dir_count: int = 0
    total_lines: int = 0


class RepoScannerService:
    PRIORITY_NAMES = {
        "README.md",
        "readme.md",
        "main.py",
        "app.py",
        "index.ts",
        "index.js",
        "server.py",
        "Dockerfile",
        "package.json",
        "pyproject.toml",
        "requirements.txt",
    }

    def scan(self, repo_path: Path) -> ScanResult:
        settings = get_settings()
        result = ScanResult()
        language_counter: Counter[str] = Counter()
        dir_paths: set[str] = set()

        for path in repo_path.rglob("*"):
            if should_ignore_path(path.relative_to(repo_path)):
                continue

            rel_path = str(path.relative_to(repo_path)).replace("\\", "/")

            if path.is_dir():
                dir_paths.add(rel_path)
                continue

            if not path.is_file():
                continue

            result.file_count += 1
            ext = path.suffix.lower()
            if ext in LANGUAGE_MAP:
                language_counter[LANGUAGE_MAP[ext]] += 1

            if self._is_metadata_file(rel_path):
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    if len(content) <= settings.max_file_size_bytes:
                        result.metadata_content[rel_path] = content[:4000]
                except OSError as exc:
                    logger.debug("Could not read metadata file %s: %s", rel_path, exc)

            if not is_source_file(path):
                continue

            try:
                size = path.stat().st_size
                if size > settings.max_file_size_bytes:
                    continue
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            lines = count_lines(content)
            result.total_lines += lines
            priority = self._file_priority(rel_path, path.name)

            result.files.append(
                ScannedFile(
                    path=rel_path,
                    name=path.name,
                    extension=ext.lstrip("."),
                    lines=lines,
                    content=content,
                    priority=priority,
                )
            )

        result.dir_count = len(dir_paths)
        if language_counter:
            result.primary_language = language_counter.most_common(1)[0][0]
            result.languages = [lang for lang, _ in language_counter.most_common(10)]
        else:
            result.languages = ["Unknown"]

        result.files.sort(key=lambda f: (-f.priority, -f.lines))
        result.files = result.files[: settings.max_files_to_review]
        return result

    def _is_metadata_file(self, rel_path: str) -> bool:
        if rel_path in METADATA_FILES:
            return True
        return rel_path.startswith(".github/workflows/")

    def _file_priority(self, rel_path: str, name: str) -> int:
        priority = 0
        if name in self.PRIORITY_NAMES:
            priority += 10
        if "test" not in rel_path.lower() and "spec" not in rel_path.lower():
            priority += 5
        if rel_path.count("/") <= 2:
            priority += 3
        return priority
