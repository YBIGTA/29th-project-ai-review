"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { getStudySessionDetail, type StudySessionDetail } from "@/lib/api";
import { LECTURE_ID_TO_TOPIC } from "@/lib/lectures";
import ReviewDetail from "@/components/ReviewDetail";

export default function HistoryDetailPage({ params }: { params: Promise<{ sessionId: string }> }) {
  const { sessionId } = use(params);
  const [detail, setDetail] = useState<StudySessionDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStudySessionDetail(sessionId)
      .then(setDetail)
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "학습 기록을 불러오지 못했습니다."));
  }, [sessionId]);

  const topic = detail ? LECTURE_ID_TO_TOPIC[detail.lecture_id] ?? detail.lecture_id : "";
  const date = detail
    ? new Date(detail.started_at).toLocaleString("ko-KR", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-white">
      <div className="mx-auto max-w-4xl">
        <header className="mb-8 flex items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-cyan-300">{topic}</p>
            <h1 className="mt-2 text-2xl font-bold">{detail?.objective_title ?? "학습 기록"}</h1>
            {detail && <p className="mt-1 text-sm text-slate-400">{date}</p>}
          </div>
          <Link
            href="/history"
            className="rounded-full border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-slate-500"
          >
            목록으로
          </Link>
        </header>

        {error && (
          <p className="rounded-2xl border border-rose-400/30 bg-rose-400/10 p-6 text-sm text-rose-200">{error}</p>
        )}
        {!detail && !error && (
          <p className="rounded-2xl border border-slate-800 bg-slate-900 p-6 text-sm text-slate-300">
            불러오는 중입니다...
          </p>
        )}
        {detail && (
          <>
            <ReviewDetail
              data={{
                score: detail.total_score,
                passStatus: detail.pass_status,
                essential: detail.quantitative.scores.essential,
                supporting: detail.quantitative.scores.supporting,
                coverage: detail.quantitative.scores.coverage,
                segments: detail.segments,
                claims: detail.claims,
                qualitative: detail.qualitative,
              }}
            />
            <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-950 p-5">
              <h3 className="mb-3 text-lg font-semibold text-slate-300">원본 전사문</h3>
              <p className="whitespace-pre-wrap text-sm leading-7 text-slate-400">{detail.transcript_raw}</p>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
