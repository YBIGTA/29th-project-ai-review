export const TOPIC_TO_LECTURE_ID = {
  "기초통계": "basic_statistics",
  "크롤링": "crawling",
  "EDA/FE": "eda_fe",
  "시각화": "visualization",
} as const;

export const LECTURE_ID_TO_TOPIC: Record<string, string> = Object.fromEntries(
  Object.entries(TOPIC_TO_LECTURE_ID).map(([topic, lectureId]) => [lectureId, topic]),
);

export const STATUS_LABEL: Record<string, string> = {
  created: "녹음 대기",
  processing: "평가 진행 중",
  completed: "완료",
  failed: "실패",
};
