import argparse
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from sttcorrect.llm.correction import correct_with_llm
from sttcorrect.llm.groq_client import GroqLLMClient
from sttcorrect.schema import TranscriptionResult
from sttcorrect.term_db.builder import load_term_db


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    load_dotenv()
    audio_path = Path("data/voice/DB_test_full.m4a")
    term_db = load_term_db("data/term_dbs/db_course.json")
    client = OpenAI()
    with audio_path.open("rb") as audio_file:
        response = client.audio.transcriptions.create(
            model=args.model,
            file=audio_file,
            language="ko",
            response_format="text",
        )

    raw = response if isinstance(response, str) else response.text
    term_db_used = term_db.to_term_db_used()
    corrected = correct_with_llm(raw, term_db_used, GroqLLMClient())
    result = TranscriptionResult(
        session_id=f"db-test-full-{args.model}",
        topic="DB",
        transcript_raw=raw,
        transcript_corrected=corrected,
        term_db_used=term_db_used,
    )
    Path(args.out).write_text(result.model_dump_json(ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote result to {args.out}")


if __name__ == "__main__":
    main()
