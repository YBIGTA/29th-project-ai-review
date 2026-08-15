import argparse

from sttcorrect.pipeline import run_pipeline
from sttcorrect.term_db.builder import build_term_db, load_term_db


def main() -> None:
    parser = argparse.ArgumentParser(description="오디오 + 용어 DB로 STT 전사 및 LLM 보정을 실행한다.")
    parser.add_argument("--audio", required=True, help="오디오 파일 경로 (wav)")
    parser.add_argument("--term-db", help="사전 빌드된 term_db.json 경로 (권장, 재사용 가능)")
    parser.add_argument("--pdf", help="즉석으로 용어 DB를 빌드할 PDF 경로 (--term-db 대신 사용)")
    parser.add_argument("--topic", required=True, help="과목/주제 이름 (예: DB)")
    parser.add_argument("--session-id", required=True, help="세션 ID")
    parser.add_argument("--out", required=True, help="출력 result.json 경로")
    args = parser.parse_args()

    if not args.term_db and not args.pdf:
        parser.error("--term-db 또는 --pdf 중 하나는 반드시 지정해야 합니다.")

    if args.term_db:
        term_db = load_term_db(args.term_db)
    else:
        term_db = build_term_db(args.pdf, topic=args.topic)

    result = run_pipeline(
        audio_path=args.audio,
        term_db=term_db,
        session_id=args.session_id,
        topic=args.topic,
    )

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(result.model_dump_json(ensure_ascii=False, indent=2))
    print(f"Wrote result to {args.out}")


if __name__ == "__main__":
    main()
