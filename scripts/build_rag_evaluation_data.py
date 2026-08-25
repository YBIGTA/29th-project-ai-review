from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data/processed/rag.json"
RUBRIC_PATH = ROOT / "data/evaluation/rubrics/rag.json"


def T(i, ko, en="", abbr=None, aliases=None):
    return {
        "term_id": i,
        "canonical_ko": ko,
        "canonical_en": en,
        "abbreviations": abbr or [],
        "accepted_aliases": aliases or [],
        "symbols": [],
        "not_equivalent_to": [],
    }


TERMINOLOGY = [
    T("rag", "검색 증강 생성", "Retrieval-Augmented Generation", ["RAG"]),
    T("retrieval", "검색", "retrieval"), T("generation", "생성", "generation"),
    T("retriever", "검색기", "retriever"), T("generator", "생성기", "generator"),
    T("knowledge_base", "지식 베이스", "knowledge base", ["KB"]), T("corpus", "말뭉치", "corpus"),
    T("context", "문맥", "context"), T("grounding", "근거화", "grounding", aliases=["근거 기반 생성"]),
    T("hallucination", "환각", "hallucination"), T("outdated_information", "오래된 정보", "outdated information"),
    T("sparse_retrieval", "희소 검색", "sparse retrieval"), T("inverted_index", "역색인", "inverted index"),
    T("tfidf", "단어 빈도-역문서 빈도", "Term Frequency-Inverse Document Frequency", ["TF-IDF"]),
    T("dense_retrieval", "밀집 검색", "dense retrieval"), T("embedding", "임베딩", "embedding"),
    T("query_embedding", "질의 임베딩", "query embedding"), T("document_embedding", "문서 임베딩", "document embedding"),
    T("similarity", "유사도", "similarity"), T("cosine_similarity", "코사인 유사도", "cosine similarity"),
    T("dot_product", "내적", "dot product", aliases=["inner product"]), T("euclidean_distance", "유클리드 거리", "Euclidean distance", ["L2"]),
    T("distance_concentration", "거리 집중 현상", "distance concentration"), T("representation_learning", "표현 학습", "representation learning"),
    T("self_supervised_learning", "자기지도학습", "self-supervised learning", ["SSL"]), T("word2vec", "Word2Vec", "Word2Vec"),
    T("cbow", "연속 단어 가방", "Continuous Bag of Words", ["CBOW"]), T("skipgram", "스킵그램", "Skip-gram"),
    T("contextual_embedding", "문맥 임베딩", "contextual embedding"), T("elmo", "ELMo", "Embeddings from Language Models", ["ELMo"]),
    T("bert", "BERT", "Bidirectional Encoder Representations from Transformers", ["BERT"]), T("gpt", "GPT", "Generative Pre-trained Transformer", ["GPT"]),
    T("sentence_embedding", "문장 임베딩", "sentence embedding"), T("pooling", "풀링", "pooling"),
    T("contrastive_learning", "대조 학습", "contrastive learning"), T("positive_pair", "양성 쌍", "positive pair"),
    T("negative_pair", "음성 쌍", "negative pair"), T("anisotropy", "비등방성", "anisotropy"), T("isotropy", "등방성", "isotropy"),
    T("vector_database", "벡터 데이터베이스", "vector database", ["Vector DB"]),
    T("ann", "근사 최근접 이웃", "Approximate Nearest Neighbor", ["ANN"]), T("hnsw", "계층적 탐색 가능 소세계 그래프", "Hierarchical Navigable Small World", ["HNSW"]),
    T("pq", "곱 양자화", "Product Quantization", ["PQ"]), T("centroid", "중심점", "centroid"), T("quantization", "양자화", "quantization"),
    T("mteb", "대규모 텍스트 임베딩 벤치마크", "Massive Text Embedding Benchmark", ["MTEB"]), T("top_k", "상위 K개", "top-k"),
    T("precision", "정밀도", "precision"), T("recall", "재현율", "recall"), T("chunk", "청크", "chunk"),
    T("semantic_chunking", "의미 기반 청킹", "semantic chunking"), T("overlap", "중첩", "overlap"), T("graph_chunking", "그래프 기반 청킹", "graph-based chunking"),
    T("graph_rag", "그래프 RAG", "Graph RAG"), T("entity", "개체", "entity"), T("relationship", "관계", "relationship"), T("community", "커뮤니티", "community"),
    T("hybrid_rag", "하이브리드 RAG", "Hybrid RAG"), T("knowledge_graph", "지식 그래프", "knowledge graph"),
    T("self_rag", "자기 교정형 RAG", "self-reflective RAG", ["Self-RAG"]), T("query_rewrite", "질의 재작성", "query rewriting"),
    T("feedback_loop", "피드백 루프", "feedback loop"), T("contextual_retrieval", "문맥 검색", "contextual retrieval"),
    T("situated_context", "위치 문맥", "situated context"), T("chunk_prepending", "청크 앞 문맥 추가", "chunk prepending"),
    T("hybrid_search", "하이브리드 검색", "hybrid search"), T("rank_fusion", "순위 융합", "rank fusion"),
    T("reranking", "재순위화", "reranking"), T("citation", "출처 인용", "citation"),
]


TITLES = [
    "RAG 강의 표지", "강의 목차", "RAG 소개", "RAG 질문", "LLM의 한계", "RAG 정의",
    "RAG 아키텍처", "전체 RAG 흐름", "Retriever", "Sparse Retrieval", "Dense Retrieval", "유사도와 거리",
    "표현 학습", "Representation Learning", "Word2Vec", "Contextual Embedding", "Sentence Embedding", "Contrastive Learning",
    "검색 벡터 요약", "Vector Database", "HNSW", "Product Quantization", "Embedding Benchmark", "Generator",
    "근거 기반 생성", "RAG Techniques", "Basic RAG 한계", "Graph RAG", "Hybrid RAG", "Self-Reflective RAG",
    "Chunking", "Contextual Retrieval", "Hybrid Search와 Reranking", "Contextual RAG 전체 흐름", "강의 마무리",
]

CONTENT = {
    1: "Retrieval-Augmented Generation 강의 표지이다.",
    2: "강의는 RAG 소개, architecture, retrieval representation·vector DB, generator와 advanced technique 순으로 구성된다.",
    3: "RAG 개념 도입 섹션의 구분 페이지이다.",
    4: "LLM이 학습 이후의 정보나 private domain knowledge를 어떻게 답하고, 답변 근거를 어떻게 제시할지 질문한다.",
    5: "Parametric knowledge만 사용하는 LLM은 최신성, private data 접근, 사실 근거와 hallucination 측면에서 한계가 있다. Fine-tuning과 prompt만으로 모든 지식 갱신·출처 문제를 해결할 수는 없다.",
    6: "RAG는 query와 관련된 external knowledge를 검색해 context로 제공한 뒤 model이 이를 사용해 답을 생성하는 구조다. Retrieval 품질과 grounding 지시가 최종 답의 품질을 좌우한다.",
    7: "RAG architecture 섹션의 구분 페이지이다.",
    8: "Document corpus를 chunk·embedding해 index에 저장하고, query를 같은 representation space로 변환해 relevant chunk를 찾은 뒤 generator prompt에 넣어 response를 만드는 end-to-end 흐름이다.",
    9: "Retriever는 user query와 knowledge base 사이에서 candidate document·chunk를 찾으며 sparse 또는 dense retrieval과 vector database를 사용할 수 있다.",
    10: "Sparse retrieval은 term occurrence를 기반으로 TF-IDF 같은 weight와 inverted index를 사용해 query keyword와 document를 matching한다. Exact term에는 강하지만 synonym·paraphrase에는 약할 수 있다.",
    11: "Dense retrieval은 query와 document를 embedding vector로 바꾸고 semantic similarity로 이웃을 찾는다. Paraphrase를 찾을 수 있지만 embedding model·domain과 index quality에 의존한다.",
    12: "Vector 비교에는 cosine similarity, dot product, Euclidean distance 등이 있다. 적합한 metric은 embedding의 training objective와 normalization·index 설정에 맞춰야 하며, 고차원 거리 집중이 Euclidean distance를 언제나 무효화하는 것은 아니다.",
    13: "Text representation을 sparse vector에서 distributed embedding으로 확장하는 섹션 도입이다.",
    14: "Representation learning은 task에 유용한 feature를 data로부터 학습하며 self-supervised objective는 label 없이 input structure에서 training signal을 만든다.",
    15: "Word2Vec의 CBOW는 주변 단어로 중심 단어를, Skip-gram은 중심 단어로 주변 단어를 예측해 static word vector를 학습한다. 같은 단어는 문맥이 달라도 하나의 vector를 공유한다.",
    16: "ELMo·BERT·GPT 같은 contextual model은 주변 token context에 따라 token representation을 달리한다. Bidirectional·causal 등 context 사용 방식은 architecture와 objective마다 다르다.",
    17: "Sentence embedding은 문장 전체를 fixed-size vector로 표현한다. Token representation pooling 또는 sentence-level objective를 사용할 수 있으며 모든 language model이 입력 문장을 자동으로 좋은 retrieval vector로 만드는 것은 아니다.",
    18: "Contrastive learning은 related positive pair는 가깝게, unrelated negative pair는 멀게 학습해 retrieval space를 개선한다. Representation anisotropy를 줄일 수 있지만 완전한 isotropy를 보장하지 않는다.",
    19: "Corpus document와 query를 compatible vector로 표현하고 similarity top-k를 찾는 retrieval 요약이다. Corpus embedding은 미리 계산할 수 있고 model·preprocessing version을 함께 관리해야 한다.",
    20: "Vector database는 embedding과 metadata를 저장하고 ANN index로 nearest-neighbor search를 지원한다. HNSW와 Product Quantization은 각각 빠른 graph search와 memory compression에 쓰인다.",
    21: "HNSW는 여러 layer의 proximity graph에서 상위 layer로 coarse navigation 후 하위 layer에서 candidate를 확장하는 ANN 방식이다. 빠른 empirical search와 recall-memory trade-off를 제공하지만 모든 data에서 strict O(log N) 또는 exact accuracy를 보장하지 않는다.",
    22: "Product Quantization은 vector를 subvector로 나누고 각 부분을 codebook centroid ID로 치환하는 lossy compression이다. Memory와 distance computation을 줄이는 대신 quantization error와 recall 손실이 생길 수 있다.",
    23: "MTEB는 retrieval·classification·clustering 등 여러 embedding task를 비교하는 benchmark다. Leaderboard 순위만 보지 말고 target language, domain, task, latency·cost를 자체 data로 검증해야 한다.",
    24: "Generator 섹션의 구분 페이지이다.",
    25: "Generator는 retrieved chunk와 query를 prompt context로 받아 answer를 만든다. Retrieved context도 부정확할 수 있으므로 source attribution, conflict handling과 answer grounding이 필요하다.",
    26: "RAG technique 섹션의 구분 페이지이다.",
    27: "Basic RAG는 query를 한 번 검색해 top-k context로 답하지만 bad chunk boundary, query-document mismatch, irrelevant retrieval과 context overload로 성능이 떨어질 수 있다.",
    28: "Graph RAG는 text에서 entity와 relationship을 추출해 graph를 만들고 community·subgraph 정보를 활용해 multi-hop 또는 global relation question을 검색한다. Extraction·entity linking 비용과 오류를 관리해야 한다.",
    29: "Hybrid RAG는 vector semantic retrieval과 knowledge graph의 explicit relation 탐색을 결합한다. Graph query가 반드시 entity 문자열을 직접 포함해야 하는 것은 아니며 entity linking과 query planning 방식에 따라 달라진다. 출처가 없는 benchmark 수치는 평가 근거에서 제외한다.",
    30: "강의의 Self-RAG는 initial retrieval·answer를 평가해 부족하면 query rewrite와 re-retrieval을 반복하는 corrective feedback pattern으로 설명된다. 실제 구현에는 quality criterion, retry budget과 stop condition이 필요하며 특정 논문의 고유 algorithm과 동일하다고 단정하지 않는다.",
    31: "Chunking은 document를 retrieval unit으로 나누는 과정이다. Semantic boundary, overlap, graph-based grouping 등 방법이 있으며 chunk size·overlap은 recall, precision, context continuity, duplication과 cost 사이의 trade-off다.",
    32: "Contextual retrieval은 각 chunk 앞에 document 안에서의 위치와 주제를 설명하는 short situated context를 붙여 독립 chunk가 잃은 배경을 보완한다. 추가 context가 사실과 맞고 query를 압도하지 않도록 검증해야 한다.",
    33: "Hybrid search는 sparse lexical score와 dense semantic score를 결합하고 rank fusion으로 candidate를 합친다. Reranker는 query-chunk pair를 더 정밀하게 재평가해 generator에 줄 문맥을 좁힌다.",
    34: "Corpus를 chunking한 뒤 situated context를 생성하고 embedding index와 TF-IDF index를 함께 만든다. Query 때 두 검색 결과를 rank fusion하고 top candidate를 reranking해 generator context로 전달한다.",
    35: "RAG 강의 종료 페이지이다.",
}

DIVIDERS = {3, 7, 24, 26}
ROLES = {1: "cover", 2: "table_of_contents", 35: "closing", **{p: "section_divider" for p in DIVIDERS}}


def curated_page(page):
    title = TITLES[page - 1]
    role = ROLES.get(page, "core_content")
    visual = f"{title}의 component·flow·comparison을 diagram과 text로 제시한다." if role == "core_content" else f"{title} 페이지이다."
    return [{"topic": title, "concepts": [title], "visual_description": visual, "content": CONTENT[page]}]


CURATION = {page: curated_page(page) for page in range(1, 36)}


def U(i, page, kind, quote, explanation, terms, source_type="text"):
    return {"unit_id": i, "page": page, "type": kind, "source_type": source_type, "source_excerpt": quote,
            "normalized_explanation": explanation, "source_status": "verified", "term_ids": terms}


UNITS = [
    U("rag_p5_limits", 5, "diagnostic", "LLM의 한계 / 최신 정보 / Private Data / Hallucination", "Parametric LLM만으로 최신·private·근거 문제를 해결하기 어렵다.", ["hallucination", "outdated_information", "knowledge_base"]),
    U("rag_p6_definition", 6, "definition", "외부 지식 베이스에서 관련 정보를 검색하고 이를 바탕으로 답변을 생성", "RAG의 retrieval-then-generation 정의다.", ["rag", "retrieval", "generation", "knowledge_base", "context", "grounding"]),
    U("rag_p8_pipeline", 8, "procedure", "Documents → Chunking → Embedding → Vector DB / Query → Retrieval → LLM → Answer", "Indexing과 query-time generation을 잇는 전체 흐름이다.", ["corpus", "chunk", "embedding", "vector_database", "retriever", "generator", "top_k"], "visual"),
    U("rag_p9_retriever", 9, "definition", "Query와 관련된 문서를 Knowledge Base에서 검색", "Retriever의 candidate selection 역할이다.", ["retriever", "retrieval", "knowledge_base"]),
    U("rag_p10_sparse", 10, "comparison", "Sparse Retrieval / TF-IDF / Inverted Index / Keyword", "Lexical sparse retrieval의 특징이다.", ["sparse_retrieval", "tfidf", "inverted_index"]),
    U("rag_p11_dense", 11, "comparison", "Dense Retrieval / Query Embedding / Document Embedding / Semantic Similarity", "Semantic dense retrieval의 특징이다.", ["dense_retrieval", "query_embedding", "document_embedding", "embedding", "similarity"]),
    U("rag_p12_metrics", 12, "comparison", "Cosine Similarity / Inner Product / Euclidean Distance", "Embedding 조건에 맞춰 similarity metric을 선택한다.", ["cosine_similarity", "dot_product", "euclidean_distance", "distance_concentration", "similarity"]),
    U("rag_p14_representation", 14, "definition", "Representation Learning / Self-Supervised Learning", "Data structure에서 useful representation을 학습한다.", ["representation_learning", "self_supervised_learning"]),
    U("rag_p15_word2vec", 15, "comparison", "CBOW: Context → Target / Skip-gram: Target → Context", "Word2Vec objective와 static embedding 한계다.", ["word2vec", "cbow", "skipgram", "embedding"], "visual"),
    U("rag_p16_contextual", 16, "comparison", "ELMo / BERT / GPT / Contextualized Embedding", "Context-dependent token representation이다.", ["contextual_embedding", "elmo", "bert", "gpt"]),
    U("rag_p17_sentence", 17, "definition", "Sentence Embedding / 문장 전체를 하나의 벡터", "Sentence-level fixed-size representation이다.", ["sentence_embedding", "pooling", "embedding"]),
    U("rag_p18_contrastive", 18, "procedure", "Positive Pair는 가깝게 / Negative Pair는 멀게", "Contrastive objective로 retrieval space를 조정한다.", ["contrastive_learning", "positive_pair", "negative_pair", "anisotropy", "isotropy"]),
    U("rag_p20_vectordb", 20, "definition", "Vector Database / HNSW / Product Quantization", "Vector DB와 ANN·compression index를 구분한다.", ["vector_database", "ann", "hnsw", "pq"]),
    U("rag_p21_hnsw", 21, "procedure", "상위 레이어부터 탐색하고 하위 레이어에서 정교하게 검색", "HNSW의 hierarchical graph navigation이다.", ["hnsw", "ann", "recall"], "visual"),
    U("rag_p22_pq", 22, "procedure", "1024차원 벡터를 8개의 Subvector로 분할 / Centroid ID로 저장", "PQ의 lossy subvector quantization 예다.", ["pq", "quantization", "centroid", "recall"], "visual"),
    U("rag_p23_mteb", 23, "comparison", "MTEB / Embedding Model Leaderboard", "Target task·language·domain에 맞춰 embedding model을 평가한다.", ["mteb", "embedding", "retrieval"]),
    U("rag_p25_generator", 25, "procedure", "Query + Retrieved Documents → LLM → Answer", "Generator가 retrieved context를 사용해 grounded answer를 만든다.", ["generator", "context", "grounding", "citation"], "visual"),
    U("rag_p27_basic_limit", 27, "diagnostic", "Retrieval Quality가 낮으면 잘못된 Context / Chunking이 부적절하면 정보 손실", "Basic RAG의 retrieval·chunking failure mode다.", ["retrieval", "chunk", "precision", "recall"]),
    U("rag_p28_graph", 28, "procedure", "Entity·Relationship 추출 → Graph 구축 → Community Detection", "Graph RAG가 relation structure를 검색에 사용한다.", ["graph_rag", "entity", "relationship", "knowledge_graph", "community"]),
    U("rag_p29_hybrid", 29, "comparison", "Vector DB + Knowledge Graph", "Hybrid RAG는 semantic vector와 explicit graph relation을 결합한다.", ["hybrid_rag", "vector_database", "knowledge_graph", "entity", "relationship"]),
    U("rag_p30_feedback", 30, "procedure", "Answer 평가 → Query Rewrite → Retrieval 재수행", "Corrective/self-reflective retrieval loop다.", ["self_rag", "query_rewrite", "feedback_loop", "retrieval"]),
    U("rag_p31_chunking", 31, "comparison", "Semantic Chunking / Overlap / Graph-based Chunking", "Chunk boundary와 overlap의 trade-off다.", ["chunk", "semantic_chunking", "overlap", "graph_chunking", "precision", "recall"]),
    U("rag_p32_contextual", 32, "procedure", "각 Chunk 앞에 문서 내 위치·맥락을 설명하는 짧은 Context 추가", "Situated context를 chunk에 prepend한다.", ["contextual_retrieval", "situated_context", "chunk_prepending", "chunk"]),
    U("rag_p33_hybrid_search", 33, "procedure", "Sparse + Dense Retrieval → Rank Fusion → Reranking", "Lexical·semantic candidate를 합치고 reranker로 정제한다.", ["hybrid_search", "sparse_retrieval", "dense_retrieval", "rank_fusion", "reranking"]),
    U("rag_p34_contextual_flow", 34, "procedure", "Contextual Chunk → Embedding·TF-IDF Index → Rank Fusion → Reranker → Generator", "Contextual hybrid RAG의 indexing과 query flow다.", ["contextual_retrieval", "tfidf", "embedding", "rank_fusion", "reranking", "generator"], "visual"),
]


MAP = {
    "rag.limitations": ["rag_p5_limits"], "rag.definition": ["rag_p6_definition"],
    "rag.indexing_flow": ["rag_p8_pipeline"], "rag.query_flow": ["rag_p8_pipeline", "rag_p25_generator"],
    "rag.retriever_role": ["rag_p9_retriever"], "rag.sparse": ["rag_p10_sparse"], "rag.dense": ["rag_p11_dense"], "rag.sparse_dense_tradeoff": ["rag_p10_sparse", "rag_p11_dense"],
    "rag.metric_types": ["rag_p12_metrics"], "rag.metric_choice": ["rag_p12_metrics"],
    "rag.representation": ["rag_p14_representation"], "rag.word2vec": ["rag_p15_word2vec"],
    "rag.contextual": ["rag_p16_contextual"], "rag.sentence": ["rag_p17_sentence"], "rag.contrastive": ["rag_p18_contrastive"],
    "rag.vector_db": ["rag_p20_vectordb"], "rag.hnsw": ["rag_p21_hnsw"], "rag.pq": ["rag_p22_pq"],
    "rag.embedding_eval": ["rag_p23_mteb"],
    "rag.basic_failures": ["rag_p27_basic_limit"], "rag.retrieval_eval": ["rag_p27_basic_limit"],
    "rag.graph_build": ["rag_p28_graph"], "rag.graph_use": ["rag_p28_graph"],
    "rag.hybrid_rag": ["rag_p29_hybrid"], "rag.graph_limit": ["rag_p29_hybrid"],
    "rag.feedback": ["rag_p30_feedback"], "rag.feedback_stop": ["rag_p30_feedback"],
    "rag.semantic_chunks": ["rag_p31_chunking"], "rag.overlap": ["rag_p31_chunking"], "rag.chunk_tradeoff": ["rag_p31_chunking"],
    "rag.context_prepend": ["rag_p32_contextual"], "rag.context_quality": ["rag_p32_contextual"],
    "rag.hybrid_search": ["rag_p33_hybrid_search"], "rag.rank_fusion": ["rag_p33_hybrid_search"], "rag.reranking": ["rag_p33_hybrid_search", "rag_p34_contextual_flow"],
}


CRITICAL_ERRORS = {
    "rag.definition": ["RAG가 model weight를 매 query마다 재학습하는 방식이라고 설명"],
    "rag.indexing_flow": ["Query를 받기 전에 corpus를 전혀 준비하거나 index하지 않는다고 설명"],
    "rag.sparse": ["Sparse retrieval이 keyword와 term occurrence를 사용하지 않는다고 설명"],
    "rag.dense": ["Dense retrieval이 token의 exact string 일치만 비교한다고 설명"],
    "rag.metric_choice": ["Euclidean distance는 고차원에서 언제나 사용할 수 없고 cosine만 항상 정답이라고 설명"],
    "rag.word2vec": ["CBOW와 Skip-gram의 입력·예측 방향을 서로 바꿔 설명"],
    "rag.sentence": ["어떤 pretrained language model이든 별도 pooling·objective 없이 자동으로 최적 sentence retrieval vector를 만든다고 설명"],
    "rag.hnsw": ["HNSW가 모든 dataset에서 exact neighbor와 strict O(log N)을 보장한다고 설명"],
    "rag.pq": ["Product Quantization이 정보 손실 없이 원래 vector를 완전히 복원한다고 설명"],
    "rag.embedding_eval": ["MTEB 1위 model이면 모든 언어·domain·latency 조건에서 항상 최적이라고 설명"],
    "rag.graph_limit": ["질문에 entity 이름이 직접 없으면 graph retrieval이 절대 불가능하다고 설명"],
    "rag.feedback": ["Self-RAG가 무조건 한 번만 검색하고 답을 수정하지 않는 방식이라고 설명"],
    "rag.feedback_stop": ["Quality check나 stop condition 없이 만족할 때까지 무한 반복해야 한다고 설명"],
    "rag.chunk_tradeoff": ["모든 corpus와 질문에 하나의 chunk size가 항상 최적이라고 설명"],
    "rag.context_quality": ["생성한 chunk context는 사실 검증 없이 항상 정확하다고 설명"],
    "rag.reranking": ["Reranker가 corpus 전체를 처음부터 embedding index 없이 반드시 전수 검색하는 단계라고 설명"],
}


def C(i, role, text, category="explanation_application"):
    return {"claim_id": i, "role": role, "category": category, "text": text, "weight": 1.0,
            "evidence": [], "term_ids": [],
            "evaluation_criteria": {"required_elements": [text], "critical_errors": CRITICAL_ERRORS.get(i, [])}}


def S(i, title, summary, claims):
    return {"sub_objective_id": i, "title": title, "summary": summary, "claims": claims}


def O(i, title, description, subs):
    count = sum(len(s["claims"]) for s in subs)
    return {"objective_id": i, "title": title, "selection_description": description,
            "supporting_claim_slots": 2 if count <= 8 else 3, "sub_objectives": subs}


def build_rubric():
    objectives = [
        O("rag.foundations_architecture", "RAG 목적과 전체 구조", "RAG가 필요한 이유와 indexing·retrieval·generation 흐름을 설명한다.", [
            S("rag.foundation.need", "LLM 한계와 RAG", "External knowledge를 연결하는 이유를 설명한다.", [
                C("rag.limitations", "essential", "Parametric LLM은 최신·private information 접근과 source grounding에 한계가 있어 outdated answer와 hallucination이 생길 수 있다.", "core_understanding"),
                C("rag.definition", "supporting", "RAG는 query와 관련된 external knowledge를 먼저 retrieve하고 그 context를 사용해 answer를 generate하는 방식이다."),
            ]),
            S("rag.foundation.pipeline", "Indexing과 Query 흐름", "Corpus 준비부터 answer까지 연결한다.", [
                C("rag.indexing_flow", "essential", "Offline indexing에서는 corpus를 chunk로 나누고 embedding·metadata를 만들어 searchable index나 vector database에 저장한다."),
                C("rag.query_flow", "supporting", "Query time에는 query를 compatible representation으로 만들고 top-k chunk를 검색해 query와 함께 generator에 전달한다."),
                C("rag.retriever_role", "supporting", "Retriever는 knowledge base에서 relevant candidate를 고르고 generator는 retrieved evidence를 바탕으로 response를 구성한다."),
            ]),
            S("rag.foundation.retrieval", "Sparse와 Dense Retrieval", "두 검색 방식의 기준과 trade-off를 설명한다.", [
                C("rag.sparse", "essential", "Sparse retrieval은 term frequency와 inverted index 기반 lexical matching을 사용해 exact keyword에 강하다."),
                C("rag.dense", "supporting", "Dense retrieval은 query·document embedding의 semantic similarity를 사용해 synonym과 paraphrase를 찾을 수 있다."),
                C("rag.sparse_dense_tradeoff", "supporting", "Sparse는 lexical precision, dense는 semantic recall에 강점이 있지만 query·domain에 따라 결과가 달라 두 방식을 함께 사용할 수 있다."),
            ]),
        ]),
        O("rag.embeddings_vector_search", "임베딩과 벡터 검색", "Representation, metric, vector index와 model evaluation을 설명한다.", [
            S("rag.embedding.metric", "유사도 척도", "Vector comparison과 설정 조건을 설명한다.", [
                C("rag.metric_types", "essential", "Embedding neighbor search에는 cosine similarity, dot product와 Euclidean distance 같은 metric을 사용할 수 있다.", "core_understanding"),
                C("rag.metric_choice", "supporting", "Metric은 embedding training objective와 normalization·ANN index 설정에 맞춰 선택하며 normalized vector에서는 cosine과 dot product 순위가 같을 수 있다."),
            ]),
            S("rag.embedding.representation", "단어·문맥·문장 표현", "Representation 발전과 차이를 설명한다.", [
                C("rag.representation", "essential", "Representation learning은 data의 structure를 이용해 downstream task에 유용한 vector feature를 학습하며 self-supervised objective를 활용할 수 있다."),
                C("rag.word2vec", "supporting", "Word2Vec의 CBOW는 context로 target word를, Skip-gram은 target word로 context를 예측하지만 한 word에 static vector를 준다."),
                C("rag.contextual", "supporting", "ELMo·BERT·GPT 계열은 surrounding context에 따라 token representation을 바꾸며 context direction과 objective는 model마다 다르다."),
                C("rag.sentence", "supporting", "Sentence embedding은 pooling 또는 sentence-level training objective로 문장 전체를 fixed-size vector로 나타낸다."),
            ]),
            S("rag.embedding.contrastive", "대조 학습", "Retrieval space를 학습하는 원리를 설명한다.", [
                C("rag.contrastive", "essential", "Contrastive learning은 semantically related positive pair를 가깝게, unrelated negative pair를 멀게 해 retrieval-friendly embedding space를 학습한다."),
                C("rag.vector_db", "supporting", "Vector database는 embedding·metadata와 ANN index를 저장해 large corpus의 nearest-neighbor retrieval을 지원한다."),
            ]),
            S("rag.embedding.index", "HNSW·PQ와 모델 선택", "속도·memory·quality trade-off를 설명한다.", [
                C("rag.hnsw", "essential", "HNSW는 multi-layer proximity graph의 상위 layer에서 빠르게 이동하고 하위 layer에서 candidate를 정교화하는 approximate search다."),
                C("rag.pq", "supporting", "Product Quantization은 vector를 subvector로 나눠 centroid code로 저장해 memory와 계산을 줄이는 lossy compression이다."),
                C("rag.embedding_eval", "supporting", "MTEB 등 benchmark는 후보 비교에 쓰되 target language·domain·retrieval task와 latency·cost를 실제 data에서 검증해야 한다."),
            ]),
        ]),
        O("rag.advanced_retrieval", "고급 Retrieval 전략", "Basic RAG의 실패를 진단하고 graph·hybrid·feedback retrieval을 설명한다.", [
            S("rag.advanced.failure", "Basic RAG 실패와 평가", "Retrieval failure를 진단한다.", [
                C("rag.basic_failures", "essential", "Basic RAG는 bad chunk boundary, query-document mismatch, irrelevant top-k와 context overload 때문에 없는 RAG보다 답이 나빠질 수 있다.", "core_understanding"),
                C("rag.retrieval_eval", "supporting", "Retrieval은 relevant evidence의 recall과 returned context의 precision을 함께 보고 final answer grounding도 별도로 평가한다."),
            ]),
            S("rag.advanced.graph", "Graph RAG", "Entity·relationship graph를 만드는 흐름을 설명한다.", [
                C("rag.graph_build", "essential", "Graph RAG는 corpus에서 entity와 relationship을 추출·연결하고 community 또는 subgraph를 retrieval unit으로 구성한다."),
                C("rag.graph_use", "supporting", "Knowledge graph는 explicit relation과 multi-hop·global question에 도움을 줄 수 있지만 extraction과 entity linking error·cost를 관리해야 한다."),
            ]),
            S("rag.advanced.hybrid", "Hybrid RAG", "Vector와 graph 검색을 결합한다.", [
                C("rag.hybrid_rag", "essential", "Hybrid RAG는 vector semantic similarity와 knowledge graph의 explicit relationship 탐색을 결합해 서로 다른 retrieval signal을 보완한다."),
                C("rag.graph_limit", "supporting", "Graph retrieval 가능 여부는 질문의 exact entity 문자열뿐 아니라 entity linking과 query planning strategy에 달려 있다."),
            ]),
            S("rag.advanced.feedback", "교정·피드백 검색", "Answer 점검과 재검색 loop를 설명한다.", [
                C("rag.feedback", "essential", "강의의 self-reflective RAG pattern은 retrieved evidence나 draft answer를 평가하고 부족하면 query를 rewrite해 retrieval과 generation을 반복한다."),
                C("rag.feedback_stop", "supporting", "Feedback loop에는 quality criterion, retry budget과 stop·fallback condition을 두어 infinite loop와 cost 증가를 막는다."),
            ]),
        ]),
        O("rag.chunking_contextual", "Chunking과 Contextual Retrieval", "Chunk 경계, contextual prepending, hybrid search와 reranking을 설명한다.", [
            S("rag.chunk.strategy", "Chunking 전략", "Semantic boundary와 overlap을 조절한다.", [
                C("rag.semantic_chunks", "essential", "Semantic chunking은 문단·topic 변화 같은 meaning boundary를 이용해 related information을 하나의 retrieval unit으로 묶는다.", "core_understanding"),
                C("rag.overlap", "supporting", "Neighbor chunk overlap은 boundary에서 끊긴 context recall을 높일 수 있지만 duplicate result와 token·index cost를 늘린다."),
                C("rag.chunk_tradeoff", "supporting", "Chunk size와 strategy는 corpus structure, question granularity, embedding model과 generator context budget에 맞춰 evaluation으로 선택한다."),
            ]),
            S("rag.chunk.context", "Contextual Chunk", "독립 chunk의 배경을 보완한다.", [
                C("rag.context_prepend", "essential", "Contextual retrieval은 각 chunk 앞에 source document 내 위치·topic을 설명하는 short situated context를 prepend한 뒤 index한다."),
                C("rag.context_quality", "supporting", "Generated situated context는 source와 일치하는지 검증하고 지나치게 길거나 generic해 original chunk signal을 희석하지 않게 한다."),
            ]),
            S("rag.chunk.retrieve", "Hybrid Search와 Reranking", "Candidate generation과 precision refinement를 구분한다.", [
                C("rag.hybrid_search", "essential", "Hybrid search는 sparse lexical retrieval과 dense semantic retrieval을 함께 실행해 complementary candidate를 얻는다."),
                C("rag.rank_fusion", "supporting", "Rank fusion은 scale이 다른 sparse·dense result의 순위를 공통 candidate list로 결합한다."),
                C("rag.reranking", "supporting", "Reranker는 작은 candidate set의 query-document relevance를 더 정밀하게 다시 계산해 generator에 줄 context를 좁힌다."),
            ]),
        ]),
    ]
    return {
        "schema_version": "2.2.0", "lecture_id": "rag", "lecture_name": "Retrieval-Augmented Generation",
        "assessment": {"mode": "selected_topic_recall", "target_seconds": 120, "max_seconds": 120,
                       "score_policy": {"essential_points": 60, "supporting_points": 20, "coverage_points": 20}},
        "top_level_objectives": objectives,
        "excluded_source_claims": [
            {"page": 12, "chunk_id": "rag_p12_01", "source_text": "차원이 증가하면 모든 점 간 거리가 비슷해져 Euclidean Distance 사용 불가",
             "reason": "Distance concentration은 고려 요소지만 Euclidean distance가 모든 embedding·index에서 보편적으로 사용 불가한 것은 아님"},
            {"page": 17, "chunk_id": "rag_p17_01", "source_text": "문장 자체를 넣으면 바로 벡터가 나옴",
             "reason": "Useful sentence embedding은 pooling과 sentence-level objective 등 model-specific design에 의존"},
            {"page": 18, "chunk_id": "rag_p18_01", "source_text": "모든 방향으로 균일하게 분포하도록 함",
             "reason": "Contrastive learning이 anisotropy를 줄일 수 있으나 완전한 isotropy를 보장하지 않음"},
            {"page": 21, "chunk_id": "rag_p21_01", "source_text": "정확도는 유지하며 비교 횟수를 O(log N) 수준으로 감소",
             "reason": "HNSW는 approximate method이며 strict complexity와 exact recall은 dataset·parameter에 따라 보장되지 않음"},
            {"page": 29, "chunk_id": "rag_p29_01", "source_text": "Graph Query는 명시적인 Entity 정보가 있어야 작동 / 성능 비교 수치",
             "reason": "Entity linking·query planning에 따라 달라지며 benchmark 출처와 조건이 명시되지 않음"},
            {"page": 30, "chunk_id": "rag_p30_01", "source_text": "Self-RAG",
             "reason": "슬라이드는 특정 논문의 전체 algorithm보다 corrective/self-reflective retrieval loop를 포괄적으로 설명하므로 해당 범위로 평가"},
        ],
    }


def apply_evaluation_data(processed_path=PROCESSED_PATH, rubric_path=RUBRIC_PATH):
    data = json.loads(Path(processed_path).read_text())
    pages = {chunk["page"]: chunk for chunk in data["chunks"]}
    if set(pages) != set(range(1, 36)):
        raise ValueError("RAG PDF 1~35쪽이 필요합니다.")
    data["schema_version"] = "2.1.0"
    data["terminology"] = TERMINOLOGY
    for page, chunk in pages.items():
        chunk.update(page_role=ROLES.get(page, "core_content"), term_ids=[], evidence_units=[], source_issues=[])
    issues = {
        12: ("rag_p12_euclidean", "Euclidean Distance 사용 불가", "overgeneralized", "Metric은 embedding training·normalization·index 조건에 맞춰 선택한다.", "warn"),
        17: ("rag_p17_sentence", "문장 자체를 넣으면 바로 벡터가 나옴", "overgeneralized", "Pooling 또는 sentence-level objective와 model choice가 retrieval quality를 좌우한다.", "warn"),
        18: ("rag_p18_isotropy", "모든 방향으로 균일하게 분포", "overgeneralized", "Contrastive objective가 anisotropy를 완화할 수 있으나 perfect isotropy를 보장하지 않는다.", "warn"),
        21: ("rag_p21_complexity", "정확도 유지 / O(log N)", "overgeneralized", "Approximate recall과 empirical speed는 parameter·dataset에 따라 달라진다.", "exclude"),
        29: ("rag_p29_entity", "명시적인 Entity 정보가 있어야 작동", "overgeneralized", "Entity linking과 query planning으로 implicit entity도 연결할 수 있다.", "warn"),
        30: ("rag_p30_name", "Self-RAG", "ambiguous", "이 강의에서는 corrective/self-reflective feedback pattern 범위로 판정한다.", "warn"),
    }
    for page, (issue_id, source_text, issue_type, correction, policy) in issues.items():
        pages[page]["source_issues"] = [{"issue_id": issue_id, "source_text": source_text, "issue_type": issue_type,
                                          "correction": correction, "evaluation_policy": policy}]
    lookup = {}
    for raw in UNITS:
        unit = dict(raw)
        page = unit.pop("page")
        pages[page]["term_ids"] = list(dict.fromkeys(pages[page]["term_ids"] + unit["term_ids"]))
        pages[page]["evidence_units"].append(unit)
        lookup[unit["unit_id"]] = (pages[page], unit)
    Path(processed_path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    rubric = build_rubric()
    claims = {claim["claim_id"]: claim for objective in rubric["top_level_objectives"]
              for sub in objective["sub_objectives"] for claim in sub["claims"]}
    if set(claims) != set(MAP):
        raise ValueError(f"Claim mismatch: {set(claims) ^ set(MAP)}")
    for claim_id, unit_ids in MAP.items():
        terms = []
        for unit_id in unit_ids:
            chunk, unit = lookup[unit_id]
            terms += unit["term_ids"]
            claims[claim_id]["evidence"].append({
                "page": chunk["page"], "chunk_id": chunk["chunk_id"], "unit_id": unit_id,
                "source_excerpt": unit["source_excerpt"], "source_status": "verified", "review_note": "",
            })
        claims[claim_id]["term_ids"] = list(dict.fromkeys(terms))
    Path(rubric_path).parent.mkdir(parents=True, exist_ok=True)
    Path(rubric_path).write_text(json.dumps(rubric, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    apply_evaluation_data()
