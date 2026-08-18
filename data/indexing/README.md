# 임베딩 대상 관리

이 폴더는 별도 프로젝트가 아니라 기존 `project` 안에서 임베딩 대상을 관리하는
설정 영역이다. 원본 구조화 JSON을 수정하거나 일부 페이지를 삭제하지 않는다.

## 현재 선별 결과

| 강의 | 전체 Chunk | 포함 | 제외 |
| --- | ---: | ---: | ---: |
| 기초통계 | 42 | 36 | 6 |
| 크롤링 | 21 | 14 | 7 |
| EDA / FE | 42 | 35 | 7 |
| 시각화 | 39 | 32 | 7 |
| 합계 | 144 | 117 | 27 |

`embedding_manifest.json`은 기본적으로 모든 Chunk를 포함하고, 검색 가치가 낮다고
검토된 Chunk만 ID와 이유를 적어 제외한다. 자동 문자열 필터를 사용하지 않으므로
제목이 비슷하다는 이유로 실제 내용 페이지가 우연히 제외되지 않는다.

제외 이유는 표지, 목차, 내용 없는 섹션 구분, 내용 없는 실습·과제 구분, 종료
슬라이드로 제한한다. 강의안의 논쟁 가능하거나 부정확한 서술은 검색에서 삭제하지
않고 `review_flags`로 표시한다. 평가할 때는 평가 rubric의 오개념 규칙을 우선한다.

## 변경 감지

각 구조화 JSON의 SHA-256과 예상 Chunk 수를 manifest에 기록했다. 팀원이 JSON을
수정하면 dry-run이 즉시 실패하므로, 변경된 Chunk와 제외 목록을 다시 검토한 뒤
해시와 예상 수를 갱신해야 한다. 단순히 검사를 통과시키기 위해 해시만 바꾸면 안
된다.

## 실행 순서

```bash
python scripts/build_vector_db.py --dry-run
python scripts/build_vector_db.py --smoke-test --lecture-id basic_statistics
python scripts/build_vector_db.py --execute
```

첫 명령은 API와 DB를 전혀 건드리지 않는다. 두 번째 명령부터 OpenAI API 키와
API 사용 권한이 필요하다. `--smoke-test`는 Chunk 하나만 임베딩하고 저장하지
않으며, `--execute`만 실제 ChromaDB를 변경한다.

GitHub에는 `data/processed/`의 구조화 JSON, 이 폴더의 manifest와 코드를 함께
공유한다. `.env`, `vector_db/`, 실행 기록은 각 환경에서 생성되므로 커밋하지
않는다.
