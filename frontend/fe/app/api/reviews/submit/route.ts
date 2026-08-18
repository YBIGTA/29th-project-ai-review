import { NextResponse } from "next/server";

const reviewStore = new Map<string, Record<string, unknown>>();

export async function POST(request: Request) {
  const body = await request.json();
  const sessionId = body.session_id ?? `session-${Date.now()}`;
  const topic = body.topic ?? "기초통계";
  const transcript = body.transcript_raw ?? body.transcript_corrected ?? "";
  const correctedTranscript = body.transcript_corrected ?? transcript;

  const score = 86;
  const reviewId = `review-${Date.now()}`;
  const report = {
    review_id: reviewId,
    session_id: sessionId,
    score,
    transcript,
    corrected_transcript: correctedTranscript,
    feedback: {
      summary: `${topic} 주제에서 핵심 흐름을 잘 연결했습니다. 다만 사례와 비교 설명을 더 보강하면 더욱 안정적인 발표가 됩니다.`,
      strengths: [
        "핵심 개념을 한 문장으로 정리하는 능력이 좋습니다.",
        "주제별 흐름이 대체로 자연스럽게 이어졌습니다.",
      ],
      missing_points: [
        "실제 데이터 예시가 부족해 신뢰도가 약해졌습니다.",
        "한계점과 가정에 대한 설명이 더 필요합니다.",
      ],
      suggestions: [
        "각 개념마다 실제 사례를 1개씩 연결해 보세요.",
        "결론에서 주요 판단 기준을 다시 정리해 보세요.",
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

  reviewStore.set(reviewId, report);

  return NextResponse.json(report, { status: 201 });
}

export async function GET() {
  return NextResponse.json({ reviews: [...reviewStore.values()] });
}
