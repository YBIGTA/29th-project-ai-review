from __future__ import annotations

import os
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class LectureConfig:
    lecture_id: str
    lecture_name: str
    source_names: tuple[str, ...]


LECTURES: dict[str, LectureConfig] = {
    "basic_statistics": LectureConfig(
        lecture_id="basic_statistics",
        lecture_name="기초통계",
        source_names=("basic_statistics.pdf", "기초통계.pdf"),
    ),
    "crawling": LectureConfig(
        lecture_id="crawling",
        lecture_name="크롤링",
        source_names=("crawling.pdf", "크롤링.pdf"),
    ),
    "eda_fe": LectureConfig(
        lecture_id="eda_fe",
        lecture_name="EDA / FE",
        source_names=("eda_fe.pdf", "EDA&FE.pdf", "EDA_FE.pdf", "EDA:FE.pdf"),
    ),
    "visualization": LectureConfig(
        lecture_id="visualization",
        lecture_name="시각화",
        source_names=("visualization.pdf", "시각화.pdf"),
    ),
    "cs_basics": LectureConfig(
        lecture_id="cs_basics",
        lecture_name="CS 기초",
        source_names=("cs_basics.pdf", "CS기초.pdf", "CS_기초.pdf", "CS.pdf"),
    ),
    "git": LectureConfig(
        lecture_id="git",
        lecture_name="Git",
        source_names=("git.pdf", "Git.pdf"),
    ),
    "python_environment": LectureConfig(
        lecture_id="python_environment",
        lecture_name="Python / 개발환경",
        source_names=("python_environment.pdf", "Python개발환경.pdf", "Python_개발환경.pdf"),
    ),
    "web": LectureConfig(
        lecture_id="web", lecture_name="Web", source_names=("web.pdf", "Web.pdf"),
    ),
    "network_basics": LectureConfig(
        lecture_id="network_basics", lecture_name="네트워크 기초",
        source_names=("network_basics.pdf", "네트워크 기초.pdf", "네트워크기초.pdf"),
    ),
    "machine_learning": LectureConfig(
        lecture_id="machine_learning", lecture_name="Machine Learning",
        source_names=("machine_learning.pdf", "ML.pdf"),
    ),
    "deep_learning": LectureConfig(
        lecture_id="deep_learning", lecture_name="Deep Learning",
        source_names=("deep_learning.pdf", "DL.pdf"),
    ),
    "computer_vision": LectureConfig(
        lecture_id="computer_vision", lecture_name="Computer Vision",
        source_names=("computer_vision.pdf", "CV.pdf"),
    ),
    "nlp": LectureConfig(
        lecture_id="nlp", lecture_name="Natural Language Processing",
        source_names=("nlp.pdf", "NLP.pdf"),
    ),
}


@dataclass(frozen=True)
class Settings:
    project_root: Path
    raw_data_dir: Path
    legacy_data_dir: Path
    processed_dir: Path
    cache_dir: Path
    logs_dir: Path
    openai_api_key: str | None
    llm_model: str
    max_retries: int
    max_page_chars: int
    page_render_dpi: int
    vision_detail: str

    @classmethod
    def from_env(cls, *, require_api_key: bool = False) -> "Settings":
        load_dotenv(PROJECT_ROOT / ".env")
        api_key = os.getenv("OPENAI_API_KEY") or None
        if require_api_key and not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY가 없습니다. project/.env에 설정한 뒤 다시 실행하세요."
            )

        return cls(
            project_root=PROJECT_ROOT,
            raw_data_dir=PROJECT_ROOT / "data" / "raw",
            legacy_data_dir=PROJECT_ROOT / "data",
            processed_dir=PROJECT_ROOT / "data" / "processed",
            cache_dir=PROJECT_ROOT / "outputs" / "cache",
            logs_dir=PROJECT_ROOT / "outputs" / "logs",
            openai_api_key=api_key,
            llm_model=os.getenv("LLM_MODEL", "gpt-5.6-luna"),
            max_retries=_positive_int("MAX_RETRIES", 3),
            max_page_chars=_positive_int("MAX_PAGE_CHARS", 16_000),
            page_render_dpi=_positive_int("PAGE_RENDER_DPI", 160),
            vision_detail=_vision_detail(),
        )

    def ensure_output_dirs(self) -> None:
        for path in (
            self.raw_data_dir,
            self.processed_dir,
            self.cache_dir,
            self.logs_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)


def _positive_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    value = int(raw)
    if value < 1:
        raise ValueError(f"{name}은 1 이상의 정수여야 합니다.")
    return value


def _vision_detail() -> str:
    value = os.getenv("VISION_DETAIL", "original").strip().lower()
    allowed = {"low", "high", "original", "auto"}
    if value not in allowed:
        raise ValueError(f"VISION_DETAIL은 다음 중 하나여야 합니다: {sorted(allowed)}")
    return value


def _normalized(value: str) -> str:
    return unicodedata.normalize("NFC", value).casefold()


def resolve_pdf_path(settings: Settings, lecture: LectureConfig) -> Path:
    search_dirs = (
        settings.raw_data_dir,
        settings.project_root / "data" / "pdfs",
        settings.legacy_data_dir,
    )
    expected = {_normalized(name) for name in lecture.source_names}
    for directory in search_dirs:
        if not directory.exists():
            continue
        for candidate in directory.glob("*.pdf"):
            if _normalized(candidate.name) in expected:
                return candidate
    names = ", ".join(lecture.source_names)
    raise FileNotFoundError(
        f"{lecture.lecture_name} PDF를 찾을 수 없습니다. 예상 파일명: {names}"
    )
