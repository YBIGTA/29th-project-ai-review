# AWS·DB 평가 데이터 확장 기록

## 완료 범위

두 PDF의 모든 페이지를 원본 text와 slide image로 대조해 다음 산출물을 만들었다.

| 강의 | 페이지 | 상위 목표 | Claim | 주요 근거 페이지 |
|---|---:|---:|---:|---|
| AWS | 25 | 3 | 26 | p4-10, p13-22 |
| Database | 57 | 4 | 36 | p6, p10-31, p33-45, p47-56 |

- `data/processed/aws.json`, `data/processed/db.json`: schema 2.1, 전체 페이지 원문,
  검수 content, 한·영 용어, atomic Evidence, source issue
- `data/evaluation/rubrics/aws.json`, `data/evaluation/rubrics/db.json`: schema 2.2,
  120초 선택 목표 평가, claim별 evidence·용어·critical error
- `scripts/build_aws_evaluation_data.py`, `scripts/build_db_evaluation_data.py`: 동일 결과 재생성

표지·목차·섹션 구분·마무리 페이지는 `page_role`로 분리해 평가 Evidence로 사용하지
않는다. SQL code, table 관계, AWS architecture처럼 text extraction만으로 손실될 수 있는
정보는 slide image를 함께 확인했다.

## AWS 목표

1. `aws.cloud_foundations`: 온프레미스·클라우드, IaaS/PaaS/SaaS, 공동 책임,
   migration·DevOps·elasticity
2. `aws.services_compute`: EC2·S3·RDS·Lambda·VPC·IAM, instance·AMI·EBS,
   Auto Scaling·ELB와 availability
3. `aws.network_security_deployment`: security group, SSH·HTTP(S)·TCP·UDP,
   VPC·subnet·CIDR, Docker image 배포

정답 기준에서는 AWS 일부 장애가 모든 시스템을 반드시 중단시킨다는 일반화,
outbound 전체 허용을 보편적 최선으로 보는 설명, load balancer만으로 mixed content가
해결된다는 설명, AWS에서는 TCP만 사용한다는 설명을 제외하거나 교정했다.

## Database 목표

1. `db.foundations_rdbms`: DB·DBMS, 관계형 table·key·cardinality, integrity·constraint
2. `db.normalization_transactions`: anomaly, 1NF·2NF·3NF·고차 정규형, transaction·ACID
3. `db.sql_queries`: SQL category, DDL·DML, SELECT logical order, JOIN·UNION
4. `db.systems_selection`: OLTP·OLAP, RDBMS trade-off, NoSQL model, vector search와 DB 선택

정답 기준에서는 NoSQL을 “규칙 없음·언제나 빠름”으로 보는 일반화, foreign key가 있으면
항상 변경·삭제 불가라는 설명, ACID의 `Duration` 오타, OLTP·OLAP의 index 수를 절대
규칙으로 보는 설명을 교정했다. FAISS는 full database가 아니라 similarity-search
library/index로, Elasticsearch는 vector 기능을 포함한 search engine으로 구분했다.

## 재생성과 검증

```bash
python scripts/build_curated_json.py aws
python scripts/build_curated_json.py db
python scripts/validate_evaluation_data.py --write-schemas
python -m pytest -q
```

현재 전체 검증 결과는 `106 passed, 1 skipped`다. 백엔드와 프론트엔드 코드는 이번
확장에서 수정하지 않았다.
