export const TOPIC_TO_LECTURE_ID = {
  "Git": "git",
  "CS기초": "cs_basics",
  "Python개발환경": "python_environment",
  "네트워크 기초": "network_basics",
  "Web 기초": "web",
  "기초통계": "basic_statistics",
  "크롤링": "crawling",
  "시각화": "visualization",
  "EDA/FE": "eda_fe",
  "DL": "deep_learning",
  "ML": "machine_learning",
  "CV": "computer_vision",
  "NLP": "nlp",
  "Docker": "docker",
  "LLM": "llm",
  "AWS": "aws",
  "DB": "db",
  "AI Agent": "ai_agent",
  "RAG": "rag",
} as const;

export const LECTURE_ID_TO_TOPIC: Record<string, string> = Object.fromEntries(
  Object.entries(TOPIC_TO_LECTURE_ID).map(([topic, lectureId]) => [lectureId, topic]),
);

export const STT_SUPPORTED_TOPICS = Object.keys(TOPIC_TO_LECTURE_ID) as Array<keyof typeof TOPIC_TO_LECTURE_ID>;

export const STATUS_LABEL: Record<string, string> = {
  created: "녹음 대기",
  processing: "평가 진행 중",
  completed: "완료",
  failed: "실패",
};
