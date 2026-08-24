export const TOPIC_TO_LECTURE_ID = {
  "기초통계": "basic_statistics",
  "크롤링": "crawling",
  "EDA/FE": "eda_fe",
  "시각화": "visualization",
  "CS 기초": "cs_basics",
  "Python 개발환경": "python_environment",
  "Git": "git",
  "웹 기초": "web",
  "네트워크 기초": "network_basics",
  "머신러닝": "machine_learning",
  "딥러닝": "deep_learning",
  "컴퓨터 비전": "computer_vision",
  "자연어 처리": "nlp",
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
