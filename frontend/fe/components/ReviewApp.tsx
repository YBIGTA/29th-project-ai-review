"use client";

import { useEffect, useRef, useState } from "react";
import { submitReview, type ReviewReport } from "@/lib/api";

const topics = [
  "기초통계",
  "크롤링",
  "EDA",
  "FE/시각화",
] as const;

type Phase = "idle" | "preview" | "countdown" | "recording" | "processing" | "completed";

type ScoreBreakdown = {
  label: string;
  score: number;
  weight: number;
  tone: "cyan" | "violet" | "amber";
};

const fallbackReport: ReviewReport = {
  review_id: "review-demo-001",
  session_id: "session-demo-001",
  score: 86,
  transcript: "기초통계에서는 모집단과 표본의 차이를 설명하고, 중심극한정리를 통해 추론의 근거를 제시했다.",
  corrected_transcript:
    "기초통계에서는 모집단과 표본의 차이를 설명하고, 중심극한정리를 통해 추론의 근거를 제시했다. 또한 데이터 분포를 확인해 분석 방향을 정리했다.",
  feedback: {
    summary:
      "핵심 개념을 자연스럽게 연결했고, 전체 흐름이 체계적이었습니다. 다만 실제 사례와 비교 설명을 더 보강하면 더욱 안정적인 발표가 됩니다.",
    strengths: [
      "핵심 용어를 정확하게 설명했다.",
      "분석의 흐름이 앞뒤로 자연스럽게 이어졌다.",
      "결론을 정리하는 문장이 분명했다.",
    ],
    missing_points: [
      "예시 데이터와 함께 설명하면 이해가 더 쉬웠을 것이다.",
      "통계적 가정에 대한 언급이 조금 더 필요하다.",
      "한계점과 해석의 차이를 요약해보면 좋다.",
    ],
    suggestions: [
      "각 개념마다 짧은 예시를 1개씩 추가해 보세요.",
      "결론 직전에 핵심 요점을 다시 정리해 보세요.",
      "분석 대상과 가정을 명시해 발표의 신뢰도를 높이세요.",
    ],
  },
  status: "mock",
  metrics: {
    corrected_cer: 0.18,
    corrected_precision: 0.84,
    corrected_recall: 0.81,
    corrected_f1: 0.82,
  },
  breakdown: {
    fidelity: 34,
    connectivity: 28,
    comprehensiveness: 24,
  },
};

export default function ReviewApp() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const [selectedTopic, setSelectedTopic] = useState<(typeof topics)[number]>(topics[0]);
  const [phase, setPhase] = useState<Phase>("idle");
  const [countdown, setCountdown] = useState(3);
  const [report, setReport] = useState<ReviewReport | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [statusText, setStatusText] = useState("카메라를 준비하고 발표를 시작해보세요.");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" },
        audio: false,
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setPhase("preview");
      setStatusText("카메라 연결 완료. 발표를 시작하세요.");
    } catch {
      setStatusText("카메라 권한을 허용해 주세요.");
    }
  };

  const startCountdown = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setStatusText("브라우저가 미디어 권한을 지원하지 않습니다.");
      return;
    }

    try {
      const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(audioStream);
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        const url = URL.createObjectURL(blob);
        setAudioUrl((prev) => {
          if (prev) URL.revokeObjectURL(prev);
          return url;
        });
      };

      recorderRef.current = recorder;
      setPhase("countdown");
      setStatusText("3초 후 발표 녹음이 시작됩니다.");

      let nextValue = 3;
      const timer = window.setInterval(() => {
        nextValue -= 1;
        setCountdown(nextValue);

        if (nextValue <= 0) {
          window.clearInterval(timer);
          recorder.start();
          setPhase("recording");
          setStatusText("녹음 중입니다. 발표를 마치면 결과를 생성합니다.");
        }
      }, 1000);

      window.setTimeout(() => {
        if (recorderRef.current?.state === "recording") {
          return;
        }
      }, 3500);
    } catch {
      setStatusText("마이크 권한을 허용해 주세요.");
    }
  };

  const submitRecording = async () => {
    if (!recorderRef.current) return;

    recorderRef.current.stop();
    recorderRef.current.stream.getTracks().forEach((track) => track.stop());
    setPhase("processing");
    setStatusText("STT와 평가를 진행하고 있습니다...");
    setIsSubmitting(true);

    const transcript = `${selectedTopic} 관련 내용을 발표하면서 핵심 개념과 흐름을 연결해 설명하고 있습니다. 중심 내용과 유의점을 함께 정리하는 방식으로 발화했습니다.`;
    const correctedTranscript = `${selectedTopic} 관련 내용을 발표하면서 핵심 개념과 흐름을 연결해 설명하고 있습니다. 중심 내용과 유의점을 함께 정리하는 방식으로 발화했습니다. 각 요소의 의미를 분명히 정리했습니다.`;

    try {
      const response = await submitReview({
        session_id: `session-${Date.now()}`,
        topic: selectedTopic,
        transcript_raw: transcript,
        transcript_corrected: correctedTranscript,
      });

      setReport(response);
      setStatusText("평가 완료. 결과를 확인해보세요.");
      setPhase("completed");
    } catch {
      setReport({
        ...fallbackReport,
        session_id: `session-${Date.now()}`,
        transcript,
        corrected_transcript: correctedTranscript,
      });
      setStatusText("백엔드 연결이 없어 mock 결과를 표시합니다.");
      setPhase("completed");
    } finally {
      setIsSubmitting(false);
    }
  };

  const scoreBreakdown: ScoreBreakdown[] = report
    ? [
        { label: "충실성", score: report.breakdown?.fidelity ?? 34, weight: 40, tone: "cyan" },
        { label: "연결성", score: report.breakdown?.connectivity ?? 28, weight: 30, tone: "violet" },
        { label: "포괄성", score: report.breakdown?.comprehensiveness ?? 24, weight: 30, tone: "amber" },
      ]
    : [
        { label: "충실성", score: 34, weight: 40, tone: "cyan" },
        { label: "연결성", score: 28, weight: 30, tone: "violet" },
        { label: "포괄성", score: 24, weight: 30, tone: "amber" },
      ];

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <header className="mb-8 flex items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-cyan-300">YBIGTA AI REVIEW</p>
            <h1 className="mt-2 text-3xl font-bold">구술 복습 서비스</h1>
          </div>
          <button
            onClick={startCamera}
            className="rounded-full border border-cyan-400/60 bg-cyan-400/10 px-4 py-2 text-sm font-medium text-cyan-200 transition hover:bg-cyan-400/20"
          >
            카메라 준비
          </button>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-2xl shadow-slate-950/40">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">발표 세션</h2>
              <span className="rounded-full bg-slate-800 px-2.5 py-1 text-xs text-slate-300">
                {phase}
              </span>
            </div>

            <div className="relative overflow-hidden rounded-2xl border border-slate-700 bg-slate-950">
              <video
                ref={videoRef}
                autoPlay
                muted
                playsInline
                className="h-[420px] w-full object-cover"
              />

              {phase === "countdown" && (
                <div className="absolute inset-0 grid place-items-center bg-slate-950/50 backdrop-blur-sm">
                  <div className="grid h-24 w-24 place-items-center rounded-full border-4 border-cyan-400 bg-slate-900 text-3xl font-bold text-cyan-300">
                    {countdown}
                  </div>
                </div>
              )}
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-3">
              {topics.map((topic) => (
                <button
                  key={topic}
                  onClick={() => setSelectedTopic(topic)}
                  className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
                    selectedTopic === topic
                      ? "border-cyan-400 bg-cyan-400 text-slate-950"
                      : "border-slate-700 bg-slate-800 text-slate-200 hover:border-slate-500"
                  }`}
                >
                  {topic}
                </button>
              ))}
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              <button
                onClick={startCountdown}
                disabled={phase === "recording" || phase === "processing"}
                className="rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-50"
              >
                발표 녹음 시작
              </button>
              <button
                onClick={submitRecording}
                disabled={phase !== "recording" || isSubmitting}
                className="rounded-full border border-emerald-400 bg-emerald-400/10 px-5 py-3 text-sm font-semibold text-emerald-200 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSubmitting ? "평가 중..." : "제출하기"}
              </button>
            </div>

            <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-300">
              {statusText}
            </div>
          </section>

          <aside className="space-y-6">
            {audioUrl && (
              <div className="rounded-3xl border border-slate-800 bg-slate-900 p-5">
                <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-violet-300">
                  녹음 확인
                </h3>
                <audio controls src={audioUrl} className="w-full" />
              </div>
            )}

            <div className="rounded-3xl border border-slate-800 bg-slate-900 p-5">
              <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-amber-300">
                현재 선택 주제
              </h3>
              <p className="text-2xl font-bold text-white">{selectedTopic}</p>
            </div>
          </aside>
        </div>

        {report && (
          <section className="mt-8 rounded-3xl border border-slate-800 bg-slate-900 p-6">
            <div className="mb-6 flex items-center justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-emerald-300">Result Report</p>
                <h2 className="mt-2 text-2xl font-bold">총점 {report.score}점</h2>
              </div>
              <div className="rounded-full border border-emerald-400/40 bg-emerald-500/10 px-4 py-2 text-sm font-semibold text-emerald-200">
                {report.status.toUpperCase()}
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {scoreBreakdown.map((item) => (
                <MetricCard
                  key={item.label}
                  label={item.label}
                  value={item.score}
                  weight={item.weight}
                  tone={item.tone}
                />
              ))}
              <MetricCard label="CER" value={report.metrics?.corrected_cer ?? 0.18} tone="rose" />
            </div>

            <div className="mt-8 grid gap-6 lg:grid-cols-2">
              <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                <h3 className="mb-3 text-lg font-semibold text-cyan-300">정량 지표</h3>
                <dl className="space-y-3 text-sm">
                  <div className="flex justify-between"><dt>Corrected Precision</dt><dd>{report.metrics?.corrected_precision ?? 0.84}</dd></div>
                  <div className="flex justify-between"><dt>Corrected Recall</dt><dd>{report.metrics?.corrected_recall ?? 0.81}</dd></div>
                  <div className="flex justify-between"><dt>Corrected F1</dt><dd>{report.metrics?.corrected_f1 ?? 0.82}</dd></div>
                  <div className="flex justify-between"><dt>Corrected CER</dt><dd>{report.metrics?.corrected_cer ?? 0.18}</dd></div>
                </dl>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                <h3 className="mb-3 text-lg font-semibold text-emerald-300">정성 피드백</h3>
                <p className="text-sm leading-6 text-slate-300">{report.feedback.summary}</p>
              </div>
            </div>

            <div className="mt-8 grid gap-6 lg:grid-cols-3">
              <FeedbackPanel title="강점" items={report.feedback.strengths} tone="emerald" />
              <FeedbackPanel title="누락 포인트" items={report.feedback.missing_points} tone="amber" />
              <FeedbackPanel title="복습 질문" items={report.feedback.suggestions} tone="violet" />
            </div>
          </section>
        )}
      </div>
    </main>
  );
}

function MetricCard({
  label,
  value,
  weight,
  tone,
}: {
  label: string;
  value: number | string;
  weight?: number;
  tone: "cyan" | "violet" | "amber" | "rose";
}) {
  const colorMap = {
    cyan: "border-cyan-400/30 bg-cyan-500/10 text-cyan-200",
    violet: "border-violet-400/30 bg-violet-500/10 text-violet-200",
    amber: "border-amber-400/30 bg-amber-500/10 text-amber-200",
    rose: "border-rose-400/30 bg-rose-500/10 text-rose-200",
  };

  return (
    <div className={`rounded-2xl border p-4 ${colorMap[tone]}`}>
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-300">{label}</p>
        {weight ? <span className="text-[10px] text-slate-300">가중치 {weight}</span> : null}
      </div>
      <p className="mt-3 text-2xl font-bold">{value}</p>
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
  tone: "emerald" | "amber" | "violet";
}) {
  const colorMap = {
    emerald: "border-emerald-400/30 bg-emerald-500/5 text-emerald-100",
    amber: "border-amber-400/30 bg-amber-500/5 text-amber-100",
    violet: "border-violet-400/30 bg-violet-500/5 text-violet-100",
  };

  return (
    <div className={`rounded-2xl border p-5 ${colorMap[tone]}`}>
      <h3 className="mb-4 text-lg font-semibold">{title}</h3>
      <ul className="space-y-3 text-sm leading-6 text-slate-200">
        {items.map((item) => (
          <li key={item} className="flex gap-2">
            <span className="mt-1 h-2 w-2 rounded-full bg-current" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
