import { NextResponse } from "next/server";

const reviewStore = new Map<string, Record<string, unknown>>();

export async function POST(request: Request) {
  const body = await request.json();
  const reviewId = `review-${Date.now()}`;
  const report = {
    review_id: reviewId,
    session_id: body.session_id ?? `session-${Date.now()}`,
    lecture_id: body.lecture_id ?? "basic_statistics",
    objective_id: body.objective_id ?? "stats.hypothesis_uncertainty",
    score: 77,
    transcript: body.transcript_raw ?? "",
    corrected_transcript: body.transcript_corrected ?? body.transcript_raw ?? "",
    quantitative: {
      scores: {
        essential: { score: 48, max_score: 60, rubric_level: 3, reason: "핵심 Claim을 대체로 정확하게 설명했습니다." },
        supporting: { score: 14, max_score: 20, rubric_level: 3, reason: "보조 설명을 충분히 연결했습니다." },
        coverage: { score: 15, max_score: 20, rubric_level: 3, reason: "하위 목표 대부분을 다뤘습니다." },
      },
      total: { score: 77, max_score: 100, rubric_level: 3, reason: "Rubric Mock 결과입니다." },
      sub_objective_coverage: [],
    },
    qualitative: {
      strengths: ["핵심 개념을 정확하게 설명했습니다."],
      missing_claims: ["일부 보조 설명"],
      incorrect_claims: [],
      review_suggestions: ["빠진 하위 목표를 한 문장으로 보완해 보세요."],
    },
    status: "mock",
  };
  reviewStore.set(reviewId, report);
  return NextResponse.json(report, { status: 201 });
}

export async function GET() {
  return NextResponse.json({ reviews: [...reviewStore.values()] });
}
