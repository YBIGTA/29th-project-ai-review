import argparse
from pathlib import Path

from sttcorrect.term_db.builder import build_term_db, load_term_db, merge_term_dbs, save_term_db
from sttcorrect.term_db.collision import load_collision_seed


def main() -> None:
    parser = argparse.ArgumentParser(description="PDF에서 용어 DB(term_db.json)를 생성한다.")
    parser.add_argument("--pdf", required=True, help="강의 PDF 경로")
    parser.add_argument("--topic", default=None, help="과목/주제 이름 (예: DB)")
    parser.add_argument("--out", required=True, help="출력 term_db.json 경로")
    parser.add_argument(
        "--seed",
        default="config/seed_collision_terms.yaml",
        help="collision 분류용 curated seed yaml 경로",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="--out이 이미 존재하면 기존 term DB와 병합해 누적한다 (한 과목의 여러 PDF를 "
        "같은 --out에 계속 누적할 때 사용). --out이 없으면 처음 빌드와 동일하게 동작한다.",
    )
    args = parser.parse_args()

    term_db = build_term_db(args.pdf, topic=args.topic, seed_path=args.seed)

    if args.merge:
        out_path = Path(args.out)
        if out_path.exists():
            existing = load_term_db(args.out)
            seed = load_collision_seed(args.seed)
            term_db = merge_term_dbs([existing, term_db], seed)
        else:
            print(f"--merge given but {args.out} does not exist yet; creating a new term DB.")

    save_term_db(term_db, args.out)
    print(f"Wrote {len(term_db.entries)} terms to {args.out}")


if __name__ == "__main__":
    main()
