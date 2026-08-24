"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
  createStudySession,
  getTranscriptionStatus,
  listLearningObjectives,
  submitReview,
  transcribeAudio,
  type LearningObjective,
  type ReviewReport,
  type TranscriptionResult,
  type User,
} from "@/lib/api";
import ReviewDetail from "@/components/ReviewDetail";
import { TOPIC_TO_LECTURE_ID } from "@/lib/lectures";

const topics = Object.keys(TOPIC_TO_LECTURE_ID) as Array<keyof typeof TOPIC_TO_LECTURE_ID>;
const lectureIds = TOPIC_TO_LECTURE_ID;

type Phase = "idle" | "countdown" | "recording" | "processing" | "completed";
type ProcessStage = "idle" | "transcribing" | "correcting" | "evaluating" | "complete";

export default function ReviewApp({ user: _user }: { user: User }) {
  const audioStreamRef = useRef<MediaStream | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const recordedBlobRef = useRef<Blob | null>(null);
  const studySessionIdRef = useRef<string | null>(null);

  const [selectedTopic, setSelectedTopic] = useState<(typeof topics)[number]>(topics[0]);
  const [objectives, setObjectives] = useState<LearningObjective[]>([]);
  const [selectedObjective, setSelectedObjective] = useState<LearningObjective | null>(null);
  const [phase, setPhase] = useState<Phase>("idle");
  const [processStage, setProcessStage] = useState<ProcessStage>("idle");
  const [countdown, setCountdown] = useState(3);
  const [report, setReport] = useState<ReviewReport | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [statusText, setStatusText] = useState("주제를 선택하고 발표 녹음을 시작해보세요.");
  const [audioStream, setAudioStream] = useState<MediaStream | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    return () => {
      if (audioStreamRef.current) {
        audioStreamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  useEffect(() => {
    let cancelled = false;
    listLearningObjectives(lectureIds[selectedTopic])
      .then((result) => {
        if (cancelled) return;
        setObjectives(result);
        setSelectedObjective(result[0] ?? null);
      })
      .catch(() => {
        if (cancelled) return;
        setObjectives([]);
        setSelectedObjective(null);
        setStatusText("학습목표 목록을 불러오지 못했습니다.");
      });
    return () => {
      cancelled = true;
    };
  }, [selectedTopic]);

  const startCountdown = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setStatusText("브라우저가 미디어 권한을 지원하지 않습니다.");
      return;
    }
    if (!selectedObjective) {
      setStatusText("학습목표를 선택해 주세요.");
      return;
    }

    try {
      const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const studySession = await createStudySession(lectureIds[selectedTopic], selectedObjective.learning_objective_id);
      studySessionIdRef.current = studySession.id;
      const recorder = new MediaRecorder(audioStream);
      audioStreamRef.current = audioStream;
      setAudioStream(audioStream);
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        recordedBlobRef.current = blob;
        const url = URL.createObjectURL(blob);
        setAudioUrl((prev) => {
          if (prev) URL.revokeObjectURL(prev);
          return url;
        });
        setAudioStream(null);
      };

      recorderRef.current = recorder;
      setPhase("countdown");
      setProcessStage("idle");
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
    } catch (error) {
      console.error("녹음 준비 실패:", error);
      setStatusText("마이크 권한을 허용하거나 잠시 후 다시 시도해 주세요.");
    }
  };

  const submitRecording = async () => {
    if (!recorderRef.current || !selectedObjective || !studySessionIdRef.current) return;

    setPhase("processing");
    setProcessStage("transcribing");
    setStatusText("STT 전사 중입니다...");
    setIsSubmitting(true);
    const sessionId = studySessionIdRef.current;

    try {
      const recorder = recorderRef.current;
      const stopped = new Promise<void>((resolve) => {
        recorder.addEventListener("stop", () => resolve(), { once: true });
      });
      recorder.stop();
      recorder.stream.getTracks().forEach((track) => track.stop());
      await stopped;

      const job = await transcribeAudio(
        recordedBlobRef.current ?? new Blob(),
        sessionId,
        selectedTopic,
      );
      const transcription = await waitForTranscription(job.job_id);
      setProcessStage("evaluating");
      setStatusText("Rubric 기반 평가 중입니다...");
      const response = await submitReview({
        ...transcription,
        lecture_id: lectureIds[selectedTopic],
        objective_id: selectedObjective.objective_id,
      });

      setReport(response);
      setStatusText("평가 완료. 결과를 확인해보세요.");
      setProcessStage("complete");
      setPhase("completed");
    } catch (error) {
      console.error("STT 또는 BE 요청 실패:", error);
      setReport(null);
      setStatusText("STT 또는 Rubric 평가 연결에 실패했습니다. 백엔드 로그를 확인해 주세요.");
      setProcessStage("idle");
      setPhase("idle");
    } finally {
      setIsSubmitting(false);
    }
  };

  const waitForTranscription = async (jobId: string): Promise<TranscriptionResult> => {
    while (true) {
      const current = await getTranscriptionStatus(jobId);
      if (current.status === "transcribing") {
        setProcessStage("transcribing");
        setStatusText("STT 전사 중입니다...");
      } else if (current.status === "correcting") {
        setProcessStage("correcting");
        setStatusText("LLM이 보정 중입니다...");
      } else if (current.status === "corrected") {
        setProcessStage("correcting");
        setStatusText("LLM 보정 완료. 평가를 준비하고 있습니다...");
        return {
          job_id: current.job_id,
          session_id: current.session_id,
          topic: current.topic,
          transcript_raw: current.transcript_raw ?? "",
          transcript_corrected: current.transcript_corrected ?? "",
          term_db_used: { safe: [], content_word_collision: [], particle_collision: [] },
        };
      } else if (current.status === "failed") {
        throw new Error(current.error || "STT processing failed");
      }
      await new Promise((resolve) => window.setTimeout(resolve, 800));
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <header className="mb-8 flex items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-cyan-300">YBIGTA AI REVIEW</p>
            <h1 className="mt-2 text-3xl font-bold">구술 복습 서비스</h1>
          </div>
          <Link
            href="/history"
            className="rounded-full border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-slate-500"
          >
            학습 기록 보기
          </Link>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-2xl shadow-slate-950/40">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">발표 세션</h2>
            </div>

            <div
              className={`rounded-2xl border bg-slate-950 p-5 transition-all duration-300 ${
                phase === "recording"
                  ? "border-rose-400 shadow-[0_0_28px_rgba(251,113,133,0.3)]"
                  : "border-slate-700"
              }`}
            >
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Audio visualizer</p>
                  <p className="mt-1 text-sm text-slate-400">
                    {phase === "recording" ? "음성을 녹음하고 있습니다" : "녹음 준비가 되면 시작하세요"}
                  </p>
                </div>
                <span className={`h-3 w-3 rounded-full ${phase === "recording" ? "bg-rose-400 shadow-[0_0_12px_rgba(251,113,133,0.9)]" : "bg-slate-600"}`} />
              </div>
              <AudioVisualizer stream={audioStream} active={phase === "recording"} />
              {phase === "countdown" && (
                <div className="mt-4 flex items-center gap-3 rounded-xl border border-cyan-400/30 bg-cyan-400/5 px-4 py-3 text-cyan-200">
                  <div className="grid h-24 w-24 place-items-center rounded-full border-4 border-cyan-400 bg-slate-900 text-3xl font-bold text-cyan-300">
                    {countdown}
                  </div>
                  <p className="text-sm">잠시 후 녹음이 시작됩니다.</p>
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

            <div className="mt-4 grid gap-2 sm:grid-cols-2">
              {objectives.length === 0 && (
                <p className="text-sm text-slate-500">학습목표를 불러오는 중입니다...</p>
              )}
              {objectives.map((objective) => (
                <button
                  key={objective.learning_objective_id}
                  onClick={() => setSelectedObjective(objective)}
                  className={`rounded-xl border px-4 py-3 text-left text-sm transition ${
                    selectedObjective?.learning_objective_id === objective.learning_objective_id
                      ? "border-violet-400 bg-violet-400/15 text-violet-100"
                      : "border-slate-700 bg-slate-800 text-slate-300 hover:border-slate-500"
                  }`}
                >
                  {objective.title}
                </button>
              ))}
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              <button
                onClick={startCountdown}
                disabled={phase === "recording" || phase === "processing" || !selectedObjective}
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
              <p className="mt-2 text-sm text-violet-200">{selectedObjective?.title ?? ""}</p>
            </div>

            <ProcessPanel stage={processStage} />
          </aside>
        </div>

        {report && (
          <section className="mt-8 rounded-3xl border border-slate-800 bg-slate-900 p-6">
            <p className="mb-6 text-sm uppercase tracking-[0.2em] text-emerald-300">Result Report</p>
            <ReviewDetail
              data={{
                score: report.score,
                passStatus: report.pass_status,
                essential: report.quantitative.scores.essential,
                supporting: report.quantitative.scores.supporting,
                coverage: report.quantitative.scores.coverage,
                segments: report.segments,
                claims: report.claims,
                qualitative: report.qualitative,
              }}
            />
          </section>
        )}
      </div>
    </main>
  );
}

function AudioVisualizer({ stream, active }: { stream: MediaStream | null; active: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !stream) return;

    const context = canvas.getContext("2d");
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    let animationFrame = 0;

    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.72;
    const values = new Uint8Array(analyser.fftSize);
    source.connect(analyser);

    const draw = () => {
      const width = canvas.width;
      const height = canvas.height;
      context?.clearRect(0, 0, width, height);
      if (context) {
        context.fillStyle = "#020617";
        context.fillRect(0, 0, width, height);
        analyser.getByteTimeDomainData(values);
        // Render the recent time-domain samples from left to right. This makes
        // both ends respond to the microphone instead of mapping frequency
        // bins to the horizontal position.
        const barCount = 96;
        const barWidth = width / barCount;

        for (let index = 0; index < barCount; index += 1) {
          const start = Math.floor((index / barCount) * values.length);
          const end = Math.max(
            start + 1,
            Math.floor(((index + 1) / barCount) * values.length),
          );
          let energy = 0;
          for (let sample = start; sample < end; sample += 1) {
            const normalized = (values[sample] - 128) / 128;
            energy += normalized * normalized;
          }
          const amplitude = Math.sqrt(energy / (end - start));
          // Keep a visible bar in every horizontal slot while preserving the
          // relative movement of quiet and loud portions of the input.
          const barHeight = Math.min(height * 0.86, 12 + amplitude * height * 1.8);
          const gradient = context.createLinearGradient(0, height / 2, 0, height / 2 - barHeight / 2);
          gradient.addColorStop(0, active ? "#fb7185" : "#22d3ee");
          gradient.addColorStop(1, active ? "#fda4af" : "#a5f3fc");
          context.fillStyle = gradient;
          context.fillRect(
            index * barWidth,
            (height - barHeight) / 2,
            Math.max(1, barWidth - 1),
            barHeight,
          );
        }
      }
      animationFrame = requestAnimationFrame(draw);
    };

    draw();
    return () => {
      cancelAnimationFrame(animationFrame);
      source.disconnect();
      analyser.disconnect();
      void audioContext.close();
    };
  }, [active, stream]);

  return (
    <canvas
      ref={canvasRef}
      width={720}
      height={150}
      aria-label="음성 크기 시각화"
      className="h-32 w-full rounded-xl border border-slate-800 bg-slate-950"
    />
  );
}

function ProcessPanel({ stage }: { stage: ProcessStage }) {
  const steps: Array<{ key: Exclude<ProcessStage, "idle">; label: string }> = [
    { key: "transcribing", label: "STT 전사 중" },
    { key: "correcting", label: "LLM이 보정 중입니다" },
    { key: "evaluating", label: "Rubric 기반 평가 중" },
  ];
  const activeIndex = stage === "idle" ? -1 : stage === "complete" ? steps.length : steps.findIndex((step) => step.key === stage);

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900 p-5">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-cyan-300">진행 상황</h3>
      <ol className="space-y-3">
        {steps.map((step, index) => {
          const complete = index < activeIndex;
          const current = index === activeIndex && stage !== "complete";
          return (
            <li key={step.key} className="flex items-center gap-3 text-sm">
              <span
                className={`grid h-7 w-7 shrink-0 place-items-center rounded-full border text-xs font-semibold ${
                  current
                    ? "border-cyan-300 bg-cyan-300 text-slate-950"
                    : complete
                      ? "border-emerald-400 bg-emerald-400/15 text-emerald-300"
                      : "border-slate-700 bg-slate-800 text-slate-500"
                }`}
              >
                {complete ? "✓" : index + 1}
              </span>
              <span className={current ? "text-cyan-200" : complete ? "text-emerald-200" : "text-slate-500"}>
                {step.label}
              </span>
              {current && <span className="ml-auto h-2 w-2 animate-pulse rounded-full bg-cyan-300" />}
            </li>
          );
        })}
      </ol>
    </div>
  );
}

