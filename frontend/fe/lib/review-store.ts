export type ReviewRecord = {
  review_id: string;
  session_id: string;
  score: number;
  transcript: string;
  corrected_transcript: string;
  feedback: {
    summary: string;
    strengths: string[];
    missing_points: string[];
    suggestions: string[];
  };
  status: string;
  metrics: {
    corrected_cer: number;
    corrected_precision: number;
    corrected_recall: number;
    corrected_f1: number;
  };
};

export const reviewStore = new Map<string, ReviewRecord>();

export function buildMockReport(topic: string, transcript: string): ReviewRecord {
  const sessionId = `session-${Date.now()}`;
  const reviewId = `review-${Date.now()}`;

  const score = 81;

  return {
    review_id: reviewId,
    session_id: sessionId,
    score,
    transcript,
    corrected_transcript:
      `${transcript} 특히 ${topic}의 핵심 개념과 흐름을 연결하는 문장이 안정적으로 구성되어 있습니다. 다만 사례 설명과 한계점을 더 보강하면 발표력이 더 높아집니다.`,
    feedback: {
      summary:
        `${topic} 주제를 전달하는 데 있어 핵심 개념을 잘 연결했고, 전체 흐름이 비교적 자연스러웠습니다. 단, 실제 사례와 경계 조건을 추가하면 더 설득력 있는 발표가 됩니다.`,
      strengths: [
        "핵심 용어를 적절한 순서로 설명했다.",
        "발표의 전체 구조가 이해하기 쉽고 정돈되어 있다.",
        "결론이 핵심 메시지를 잘 되짚어 준다.",
      ],
      missing_points: [
        "실제 데이터 예시가 부족하다.",
        "가정과 한계 조건을 더 명시하면 좋다.",
        "비교와 대조의 근거를 더 넣으면 설득력이 커진다.",
      ],
      suggestions: [
        "개념 하나마다 1개의 실제 사례를 연결해 보세요.",
        "결론 전에 핵심 판단 기준을 한 번 더 정리해 보세요.",
        "한계점과 해석의 차이를 다뤄서 발표를 더 깊게 만들 수 있습니다.",
      ],
    },
    status: "mock",
    metrics: {
      corrected_cer: 0.18,
      corrected_precision: 0.84,
      corrected_recall: 0.81,
      corrected_f1: 0.82,
    },
  };
}
