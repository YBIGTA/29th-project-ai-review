"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getStudySessions, type StudySession } from "@/lib/api";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(value));
}

export default function HistoryPage() {
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStudySessions()
      .then(setSessions)
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "복습 기록을 불러오지 못했습니다."))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-white">
      <div className="mx-auto max-w-6xl">
        <header className="flex items-start justify-between gap-4">
          <div>
            <Link href="/" className="text-sm font-semibold text-cyan-300 hover:text-cyan-200">← 메인으로</Link>
            <p className="mt-8 text-sm uppercase tracking-[0.2em] text-cyan-300">Review history</p>
            <h1 className="mt-2 text-3xl font-bold">복습 기록</h1>
            <p className="mt-3 text-sm text-slate-400">지금까지 진행한 구술 복습 세션을 한눈에 확인하세요.</p>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900 px-5 py-4 text-right">
            <p className="text-xs text-slate-500">전체 세션</p>
            <p className="mt-1 text-2xl font-bold text-cyan-300">{sessions.length}</p>
          </div>
        </header>

        <section className="mt-10 overflow-hidden rounded-3xl border border-slate-800 bg-slate-900">
          <div className="hidden grid-cols-[1.1fr_1.2fr_0.9fr_0.6fr_0.8fr] gap-4 border-b border-slate-800 px-6 py-4 text-xs font-semibold uppercase tracking-[0.12em] text-slate-500 md:grid">
            <span>날짜</span><span>주제</span><span>카테고리</span><span>결과</span><span className="text-right">최종점수</span>
          </div>
          {isLoading && <p className="px-6 py-16 text-center text-sm text-slate-400">복습 기록을 불러오는 중입니다...</p>}
          {error && <p className="px-6 py-16 text-center text-sm text-rose-300">{error}</p>}
          {!isLoading && !error && sessions.length === 0 && <p className="px-6 py-16 text-center text-sm text-slate-400">아직 복습 기록이 없습니다.</p>}
          {!isLoading && !error && sessions.map((session) => (
            <div key={session.id} className="grid gap-3 border-b border-slate-800/80 px-6 py-5 last:border-b-0 md:grid-cols-[1.1fr_1.2fr_0.9fr_0.6fr_0.8fr] md:items-center md:gap-4">
              <span className="text-sm text-slate-300"><span className="mr-2 text-xs text-slate-500 md:hidden">날짜</span>{formatDate(session.completed_at ?? session.started_at)}</span>
              <span className="font-semibold text-white"><span className="mr-2 text-xs font-normal text-slate-500 md:hidden">주제</span>{session.lecture_id}</span>
              <span className="text-sm text-slate-400"><span className="mr-2 text-xs text-slate-500 md:hidden">카테고리</span>구술 복습</span>
              <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-bold ${session.status !== "completed" ? "bg-slate-800 text-slate-400" : session.pass_status === "P" ? "bg-emerald-400/15 text-emerald-300" : "bg-rose-400/15 text-rose-300"}`}>
                {session.status !== "completed" ? "진행 중" : session.pass_status}
              </span>
              <span className="font-semibold text-cyan-200 md:text-right"><span className="mr-2 text-xs font-normal text-slate-500 md:hidden">최종점수</span>{session.total_score === null ? "-" : `${session.total_score}점`}</span>
            </div>
          ))}
        </section>
      </div>
    </main>
  );
}