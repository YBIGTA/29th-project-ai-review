import argparse
from pathlib import Path

from sttcorrect.llm.organize import organize_transcript
from sttcorrect.schema import OrganizedTranscript, TranscriptionResult


def main() -> None:
    parser = argparse.ArgumentParser(
        description="1차 보정된 transcript_corrected를 기술 문서 형태로 정리한다."
    )
    parser.add_argument("--result", required=True, help="run_pipeline이 만든 result.json 경로")
    parser.add_argument("--out", required=True, help="출력 정리본 JSON 경로")
    args = parser.parse_args()

    result = TranscriptionResult.model_validate_json(Path(args.result).read_text(encoding="utf-8"))

    from sttcorrect.llm.groq_client import GroqLLMClient

    organized_text = organize_transcript(result.transcript_corrected, GroqLLMClient())
    organized = OrganizedTranscript(
        session_id=result.session_id, topic=result.topic, organized_text=organized_text
    )

    Path(args.out).write_text(organized.model_dump_json(ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote organized transcript to {args.out}")


if __name__ == "__main__":
    main()
