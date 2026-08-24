const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export type User = {
  id: string;
  google_user_id: string;
  nickname: string | null;
  profile_image_url: string | null;
};

export type AuthResponse = {
  user: User;
  expires_at: string;
};

function apiEndpoint(path: string) {
  return API_BASE_URL ? `${API_BASE_URL}${path}` : path;
}

export async function getCurrentUser(): Promise<User | null> {
  const response = await fetch(apiEndpoint("/api/auth/me"), {
    credentials: "include",
    cache: "no-store",
  });
  if (response.status === 401) return null;
  if (!response.ok) throw new Error("로그인 상태를 확인하지 못했습니다.");
  return response.json();
}

export async function loginWithGoogle(authorizationCode: string, redirectUri: string): Promise<AuthResponse> {
  const response = await fetch(apiEndpoint("/api/auth/google"), {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ authorization_code: authorizationCode, redirect_uri: redirectUri }),
  });
  if (!response.ok) throw new Error((await response.text()) || "Google 로그인에 실패했습니다.");
  return response.json();
}

export async function logout(): Promise<void> {
  const response = await fetch(apiEndpoint("/api/auth/logout"), {
    method: "POST",
    credentials: "include",
  });
  if (!response.ok) throw new Error("로그아웃에 실패했습니다.");
}

export type ReviewSubmission = {
  job_id?: string;
  session_id: string;
  topic: string;
  lecture_id: string;
  objective_id: string;
  transcript_raw: string;
  transcript_corrected: string;
  term_db_used?: {
    safe?: string[];
    content_word_collision?: string[];
    particle_collision?: string[];
  };
};

export type ScoreDetail = {
  score: number;
  max_score: number;
  rubric_level: number;
  reason: string;
};

export type ReviewSegment = {
  segment_id: string;
  index: number;
  text: string;
};

export type ClaimEvaluation = {
  claim_id: string;
  claim_text: string;
  judgment: "correct" | "mostly_correct" | "partial" | "incorrect" | "not_addressed";
  source_chunk_ids_used: string[];
  source_chunks: Array<{ source_chunk_id: string; page: number }>;
  conflict_status: string;
  evidence_spans: Array<{ segment_id: string; quote: string; relation: string }>;
  rationale: string;
};

export type QuantitativeEvaluation = {
  scores: {
    essential: ScoreDetail;
    supporting: ScoreDetail;
    coverage: ScoreDetail;
  };
  total: ScoreDetail;
  sub_objective_coverage: Array<{ sub_objective_id: string; ratio: number }>;
};

export type QualitativeEvaluation = {
  strengths: string[];
  missing_claims: string[];
  incorrect_claims: string[];
  review_suggestions: string[];
};

export type ReviewReport = {
  review_id: string;
  session_id: string;
  lecture_id: string;
  objective_id: string;
  score: number;
  pass_status: string;
  transcript: string;
  corrected_transcript: string;
  segments: ReviewSegment[];
  claims: ClaimEvaluation[];
  quantitative: QuantitativeEvaluation;
  qualitative: QualitativeEvaluation;
  status: string;
};

export type LearningObjective = {
  learning_objective_id: string;
  objective_id: string;
  title: string;
  description: string | null;
  display_order: number;
};

export type StudySessionSummary = {
  id: string;
  lecture_id: string;
  learning_objective_id: string;
  objective_title: string;
  status: string;
  pass_status: string;
  total_score: number | null;
  hint_used: boolean;
  started_at: string;
  completed_at: string | null;
};

export type StudySessionDetail = {
  id: string;
  lecture_id: string;
  objective_title: string;
  status: string;
  pass_status: string;
  total_score: number;
  started_at: string;
  completed_at: string | null;
  transcript_raw: string;
  transcript_corrected: string;
  segments: ReviewSegment[];
  claims: ClaimEvaluation[];
  quantitative: QuantitativeEvaluation;
  qualitative: QualitativeEvaluation;
};

export async function listLearningObjectives(lectureId: string): Promise<LearningObjective[]> {
  const response = await fetch(apiEndpoint(`/api/learning-objectives?lecture_id=${encodeURIComponent(lectureId)}`), {
    credentials: "include",
  });
  if (!response.ok) throw new Error((await response.text()) || "학습목표 조회에 실패했습니다.");
  const data: { objectives: LearningObjective[] } = await response.json();
  return data.objectives;
}

export async function createStudySession(lectureId: string, learningObjectiveId: string): Promise<StudySessionSummary> {
  const response = await fetch(apiEndpoint("/api/study-sessions"), {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lecture_id: lectureId, learning_objective_id: learningObjectiveId }),
  });
  if (!response.ok) throw new Error((await response.text()) || "학습 세션 생성에 실패했습니다.");
  return response.json();
}

export async function listStudySessions(): Promise<StudySessionSummary[]> {
  const response = await fetch(apiEndpoint("/api/study-sessions"), { credentials: "include", cache: "no-store" });
  if (!response.ok) throw new Error((await response.text()) || "학습 기록 조회에 실패했습니다.");
  return response.json();
}

export async function getStudySessionDetail(sessionId: string): Promise<StudySessionDetail> {
  const response = await fetch(apiEndpoint(`/api/study-sessions/${sessionId}`), { credentials: "include", cache: "no-store" });
  if (!response.ok) throw new Error((await response.text()) || "학습 기록 상세 조회에 실패했습니다.");
  return response.json();
}

export type TranscriptionResult = {
  job_id: string;
  session_id: string;
  topic: string;
  transcript_raw: string;
  transcript_corrected: string;
  term_db_used: {
    safe: string[];
    content_word_collision: string[];
    particle_collision: string[];
  };
};

export type TranscriptionJob = {
  job_id: string;
  session_id: string;
  topic: string;
  status: string;
};

export type TranscriptionStatus = TranscriptionJob & {
  transcript_raw: string | null;
  transcript_corrected: string | null;
  error: string | null;
};

export async function transcribeAudio(audio: Blob, sessionId: string, topic: string): Promise<TranscriptionJob> {
  const formData = new FormData();
  formData.append("session_id", sessionId);
  formData.append("topic", topic);
  formData.append("audio_file", audio, "review.webm");
  const response = await fetch(apiEndpoint("/api/stt/transcribe"), { method: "POST", body: formData, credentials: "include" });
  if (!response.ok) throw new Error((await response.text()) || "STT request failed");
  return response.json();
}

export async function getTranscriptionStatus(jobId: string): Promise<TranscriptionStatus> {
  const response = await fetch(apiEndpoint(`/api/stt/transcribe/${jobId}`), { credentials: "include" });
  if (!response.ok) throw new Error((await response.text()) || "Transcription status request failed");
  return response.json();
}

export async function submitReview(payload: ReviewSubmission): Promise<ReviewReport> {
  const response = await fetch(apiEndpoint("/api/reviews/submit"), {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Review submission failed");
  }

  return response.json();
}
