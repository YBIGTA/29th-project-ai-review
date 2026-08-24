import type { ReactNode } from "react";
import type { ClaimEvaluation, QualitativeEvaluation, ReviewSegment, ScoreDetail } from "@/lib/api";

export type ReviewDetailData = {
  score: number;
  passStatus: string;
  essential: ScoreDetail;
  supporting: ScoreDetail;
  coverage: ScoreDetail;
  segments: ReviewSegment[];
  claims: ClaimEvaluation[];
  qualitative: QualitativeEvaluation;
};

const JUDGMENT_LABEL: Record<ClaimEvaluation["judgment"], string> = {
  correct: "정확",
  mostly_correct: "대체로 정확",
  partial: "부분적",
  incorrect: "오개념",
  not_addressed: "언급 없음",
};

const MARK_STYLE: Record<string, string> = {
  correct: "bg-emerald-300/90 text-emerald-950",
  mostly_correct: "bg-emerald-100/90 text-emerald-950",
  partial: "bg-amber-200/90 text-amber-950",
  incorrect: "bg-rose-300/90 text-rose-950",
};

const BADGE_STYLE: Record<string, string> = {
  correct: "border-emerald-400/40 bg-emerald-500/15 text-emerald-200",
  mostly_correct: "border-emerald-300/30 bg-emerald-300/10 text-emerald-100",
  partial: "border-amber-400/40 bg-amber-500/15 text-amber-200",
  incorrect: "border-rose-400/40 bg-rose-500/15 text-rose-200",
  not_addressed: "border-slate-600 bg-slate-800 text-slate-400",
};

export default function ReviewDetail({ data }: { data: ReviewDetailData }) {
  const { score, passStatus, essential, supporting, coverage, segments, claims, qualitative } = data;
  const addressedClaims = claims.filter((claim) => claim.judgment !== "not_addressed");

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-950 p-5">
        <h2 className="text-2xl font-bold">총점 : {score.toFixed(1)} / 100점</h2>
        <span
          className={`rounded-full border px-4 py-2 text-sm font-semibold ${
            passStatus === "P"
              ? "border-emerald-400/50 bg-emerald-500/15 text-emerald-200"
              : "border-rose-400/50 bg-rose-500/15 text-rose-200"
          }`}
        >
          {passStatus === "P" ? "PASS" : "NOT PASS"}
        </span>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard label="핵심 이해도" score={essential} tone="cyan" />
        <MetricCard label="보조·심화 설명" score={supporting} tone="violet" />
        <MetricCard label="하위 목표 충족도" score={coverage} tone="amber" />
      </div>

      <Legend />

      <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
        <h3 className="mb-4 text-lg font-semibold text-violet-300">LLM 보정 전사문</h3>
        <div className="space-y-3 text-sm leading-8 text-slate-200">
          {segments.length === 0 && <p className="text-slate-500">전사 결과가 없습니다.</p>}
          {segments.map((segment) => (
            <p key={segment.segment_id} className="whitespace-pre-wrap">
              {renderHighlightedSegment(segment, claims)}
            </p>
          ))}
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
        <h3 className="mb-4 text-lg font-semibold text-cyan-300">Claim별 평가 근거</h3>
        {addressedClaims.length === 0 && <p className="text-sm text-slate-500">평가된 Claim이 없습니다.</p>}
        <ul className="space-y-4">
          {addressedClaims.map((claim) => {
            const pages = [...new Set(claim.source_chunks.map((chunk) => chunk.page))].sort((a, b) => a - b);
            return (
              <li key={claim.claim_id} className="rounded-xl border border-slate-800 bg-slate-900 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-slate-100">{claim.claim_text}</p>
                  <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${BADGE_STYLE[claim.judgment]}`}>
                    {JUDGMENT_LABEL[claim.judgment]}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-300">{claim.rationale}</p>
                {pages.length > 0 && (
                  <p className="mt-2 text-xs text-slate-500">강의자료 {pages.map((page) => `p.${page}`).join(", ")}</p>
                )}
              </li>
            );
          })}
        </ul>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <FeedbackPanel title="잘 설명한 내용" items={qualitative.strengths} tone="emerald" />
        <FeedbackPanel title="누락된 개념" items={qualitative.missing_claims} tone="amber" />
        <FeedbackPanel title="오개념" items={qualitative.incorrect_claims} tone="rose" />
      </div>
      <FeedbackPanel title="복습 제안" items={qualitative.review_suggestions} tone="violet" />
    </div>
  );
}

function renderHighlightedSegment(segment: ReviewSegment, claims: ClaimEvaluation[]) {
  type Span = { start: number; end: number; quote: string; judgment: string };
  const spans: Span[] = [];

  for (const claim of claims) {
    const style = MARK_STYLE[claim.judgment];
    if (!style) continue;
    for (const span of claim.evidence_spans) {
      if (span.segment_id !== segment.segment_id) continue;
      const start = segment.text.indexOf(span.quote);
      if (start === -1) continue;
      spans.push({ start, end: start + span.quote.length, quote: span.quote, judgment: claim.judgment });
    }
  }

  spans.sort((a, b) => a.start - b.start);
  const selected: Span[] = [];
  let cursor = 0;
  for (const span of spans) {
    if (span.start < cursor) continue;
    selected.push(span);
    cursor = span.end;
  }

  if (selected.length === 0) return segment.text;

  const nodes: ReactNode[] = [];
  let position = 0;
  selected.forEach((span, index) => {
    if (span.start > position) {
      nodes.push(segment.text.slice(position, span.start));
    }
    nodes.push(
      <mark key={`${segment.segment_id}-${index}`} className={`rounded px-0.5 ${MARK_STYLE[span.judgment]}`}>
        {span.quote}
      </mark>,
    );
    position = span.end;
  });
  if (position < segment.text.length) {
    nodes.push(segment.text.slice(position));
  }
  return nodes;
}

function Legend() {
  const items: Array<{ label: string; judgment: string }> = [
    { label: "correct!", judgment: "correct" },
    { label: "mostly correct", judgment: "mostly_correct" },
    { label: "partial", judgment: "partial" },
    { label: "incorrect", judgment: "incorrect" },
  ];
  return (
    <div className="flex flex-wrap items-center gap-5 rounded-2xl border border-slate-800 bg-slate-950 px-5 py-4 text-sm text-slate-300">
      {items.map((item) => (
        <span key={item.judgment} className="flex items-center gap-2">
          <span className={`h-4 w-6 rounded ${MARK_STYLE[item.judgment]}`} />
          {item.label}
        </span>
      ))}
    </div>
  );
}

function MetricCard({ label, score, tone }: { label: string; score: ScoreDetail; tone: "cyan" | "violet" | "amber" }) {
  const colorMap = {
    cyan: "border-cyan-400/30 bg-cyan-500/10 text-cyan-200",
    violet: "border-violet-400/30 bg-violet-500/10 text-violet-200",
    amber: "border-amber-400/30 bg-amber-500/10 text-amber-200",
  };
  return (
    <div className={`rounded-2xl border p-4 ${colorMap[tone]}`}>
      <p className="text-xs uppercase tracking-[0.2em] text-slate-300">{label}</p>
      <p className="mt-3 text-2xl font-bold">
        {score.score.toFixed(1)} / {score.max_score}
      </p>
      <p className="mt-2 text-xs leading-5 text-slate-300">{score.reason}</p>
    </div>
  );
}

function FeedbackPanel({
  title,
  items,
  tone,
}: {
  title: string;
  items: string[];
  tone: "emerald" | "amber" | "violet" | "rose";
}) {
  const colorMap = {
    emerald: "border-emerald-400/30 bg-emerald-500/5 text-emerald-100",
    amber: "border-amber-400/30 bg-amber-500/5 text-amber-100",
    violet: "border-violet-400/30 bg-violet-500/5 text-violet-100",
    rose: "border-rose-400/30 bg-rose-500/5 text-rose-100",
  };

  return (
    <div className={`rounded-2xl border p-5 ${colorMap[tone]}`}>
      <h3 className="mb-4 text-lg font-semibold">{title}</h3>
      <ul className="space-y-3 text-sm leading-6 text-slate-200">
        {items.length === 0 && <li className="text-slate-400">해당 항목이 발견되지 않았습니다.</li>}
        {items.map((item) => (
          <li key={item} className="flex gap-2">
            <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-current" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
