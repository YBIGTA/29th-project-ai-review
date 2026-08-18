import json
import re
import sys
from pathlib import Path

from nlptutti import evaluate_keywords, get_cer

REFERENCE = Path("data/reference/DB_test_full.md")

ALIASES = {
    "DB": ["데이터베이스", "DB"],
    "DBMS": ["디비엠에스", "DBMS"],
    "integrity": ["인테그리티", "무결성", "integrity"],
    "consistency": ["컨시스턴시", "정합성", "일관성", "consistency"],
    "RDBMS": ["알디비엠에스", "RDBMS"],
    "table": ["테이블", "table"],
    "row": ["로", "행", "row", "run"],
    "column": ["컬럼", "열", "column"],
    "primary key": ["프라이머리 키", "PRIMARY KEY", "Primary Key"],
    "foreign key": ["포린 키", "포린키", "FOREIGN KEY", "Foreign Key", "Falling Key"],
    "not null": ["낫 널", "NOT NULL", "NotNull"],
    "unique": ["유니크", "UNIQUE"],
    "check": ["체크", "CHECK"],
    "default": ["디폴트", "DEFAULT"],
    "update": ["업데이트", "UPDATE"],
    "set": ["셋", "SET"],
    "SQL": ["에스큐엘", "SQL"],
    "DDL": ["디디엘", "DDL"],
    "DML": ["디엠엘", "DML"],
    "DCL": ["디씨엘", "DCL"],
    "TCL": ["티씨엘", "TCL"],
    "transaction": ["트랜잭션", "TRANSACTION"],
    "commit": ["커밋", "Commit"],
    "rollback": ["롤백", "Rollback"],
    "ACID": ["애시드", "ACID"],
    "atomicity": ["애터미시티", "Atomicity"],
    "isolation": ["아이솔레이션", "Isolation"],
    "durability": ["듀레이션", "Durability"],
    "OLTP": ["올티피", "OLTP"],
    "OLAP": ["올랩", "OLAP"],
    "scale out": ["스케일 아웃", "Scale Out"],
    "NoSQL": ["노에스큐엘", "NoSQL"],
    "document store": ["다큐먼트 스토어", "Document Store"],
    "key value store": ["키밸류 스토어", "Key Value Store"],
    "wide column store": ["와이드 컬럼 스토어", "Wide Column Store"],
    "graph store": ["그래프 스토어", "Graph Store"],
    "MongoDB": ["몽고디비", "MongoDB"],
    "Redis": ["레디스", "Redis"],
    "vector DB": ["벡터 디비", "VectorDB", "Vector DB"],
}


def canonicalize(text: str) -> str:
    for canonical, variants in sorted(ALIASES.items(), key=lambda item: -max(map(len, item[1]))):
        for variant in variants:
            text = re.sub(re.escape(variant), canonical, text, flags=re.IGNORECASE)
    return text


reference = REFERENCE.read_text(encoding="utf-8")
reference = "\n".join(line[2:] if line.startswith("> ") else line for line in reference.splitlines())
if len(sys.argv) != 2:
    raise SystemExit("usage: python scripts/evaluate_db_test_full.py <result.json>")
result = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
raw = result["transcript_raw"]
corrected = result["transcript_corrected"]

print("raw CER:", get_cer(reference, raw))
print("corrected CER:", get_cer(reference, corrected))

keywords = list(ALIASES)
for label, hypothesis in (("raw", raw), ("corrected", corrected)):
    evaluation = evaluate_keywords(
        [canonicalize(reference)], [canonicalize(hypothesis)], keywords
    )
    print(label, evaluation["summary"])
