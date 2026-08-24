"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getCurrentUser, listStudySessions, type StudySessionSummary, type User } from "@/lib/api";
import { LECTURE_ID_TO_TOPIC, STATUS_LABEL } from "@/lib/lectures";

export default function HistoryPage() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [sessions, setSessions] = useState<StudySessionSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCurrentUser()
      .then((currentUser) => {
        setUser(currentUser);
        if (!currentUser) return null;
        return listStudySessions();
      })
      .then((result) => {
        if (result) setSessions(result);
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "학습 기록을 불러오지 못했습니다."))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-white">
      <div className="mx-auto max-w-4xl">
        <header className="mb-8 flex items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-cyan-300">YBIGTA AI REVIEW</p>
            <h1 className="mt-2 text-3xl font-bold">학습 기록</h1>
          </div>
          <Link
            href="/"
            className="rounded-full border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-slate-500"
          >
            복습 세션으로
          </Link>
        </header>

        {isLoading && !error && (
          <p className="rounded-2xl border border-slate-800 bg-slate-900 p-6 text-sm text-slate-300">
            로그인 상태를 확인하고 있습니다...
          </p>
        )}
        {!isLoading && !user && !error && (
          <p className="rounded-2xl border border-slate-800 bg-slate-900 p-6 text-sm text-slate-300">
            로그인이 필요합니다.{" "}
            <Link href="/" className="text-cyan-300 underline">
              홈으로 이동해 로그인해 주세요.
            </Link>
          </p>
        )}
        {error && (
          <p className="rounded-2xl border border-rose-400/30 bg-rose-400/10 p-6 text-sm text-rose-200">{error}</p>
        )}
        {user && sessions === null && !error && (
          <p className="rounded-2xl border border-slate-800 bg-slate-900 p-6 text-sm text-slate-300">
            학습 기록을 불러오는 중입니다...
          </p>
        )}
        {user && sessions !== null && sessions.length === 0 && (
          <p className="rounded-2xl border border-slate-800 bg-slate-900 p-6 text-sm text-slate-300">
            아직 완료한 복습 세션이 없습니다.
          </p>
        )}

        <div className="space-y-4">
          {sessions?.map((session) => (
            <SessionCard key={session.id} session={session} />
          ))}
        </div>
      </div>
    </main>
  );
}

function SessionCard({ session }: { session: StudySessionSummary }) {
  const topic = LECTURE_ID_TO_TOPIC[session.lecture_id] ?? session.lecture_id;
  const date = new Date(session.started_at).toLocaleString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
  const isClickable = session.status === "completed";
  const content = (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 transition hover:border-slate-600">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">{topic}</p>
          <h2 className="mt-1 text-lg font-semibold text-white">{session.objective_title}</h2>
        </div>
        <div className="flex items-center gap-2">
          {session.pass_status !== "IN_PROGRESS" && (
            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                session.pass_status === "P"
                  ? "border-emerald-400/50 bg-emerald-500/15 text-emerald-200"
                  : "border-rose-400/50 bg-rose-500/15 text-rose-200"
              }`}
            >
              {session.pass_status === "P" ? "PASS" : "NOT PASS"}
            </span>
          )}
          <span className="rounded-full border border-slate-700 bg-slate-800 px-3 py-1 text-xs text-slate-300">
            {STATUS_LABEL[session.status] ?? session.status}
          </span>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm text-slate-400">
        <span>{date}</span>
        <span className="text-lg font-bold text-slate-100">
          {session.total_score !== null ? `${session.total_score.toFixed(1)} / 100점` : "-"}
        </span>
      </div>
    </div>
  );

  if (!isClickable) return content;
  return (
    <Link href={`/history/${session.id}`} className="block">
      {content}
    </Link>
  );
}
