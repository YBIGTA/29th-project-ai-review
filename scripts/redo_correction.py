import json
import sys
from pathlib import Path

from sttcorrect.llm.correction import correct_with_llm
from sttcorrect.llm.groq_client import GroqLLMClient
from sttcorrect.term_db.builder import load_term_db


path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
term_db = load_term_db("data/term_dbs/db_course.json")
data["transcript_corrected"] = correct_with_llm(
    data["transcript_raw"], term_db.to_term_db_used(), GroqLLMClient()
)
path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Updated correction in {path}")
