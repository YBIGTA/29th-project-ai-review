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

export type StudySession = {
  id: string;
  lecture_id: string;
  status: string;
  pass_status: "P" | "NP";
  hint_used: boolean;
  started_at: string;
  completed_at: string | null;
  total_score: number | null;
};

export async function createStudySession(lectureId: string): Promise<StudySession> {
  const response = await fetch(apiEndpoint("/api/study-sessions"), {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lecture_id: lectureId }),
  });
  if (!response.ok) throw new Error("복습 세션을 생성하지 못했습니다.");
  return response.json();
}

export async function getStudySessions(): Promise<StudySession[]> {
  const response = await fetch(apiEndpoint("/api/study-sessions"), {
    credentials: "include",
    cache: "no-store",
  });
  if (response.status === 401) return [];
  if (!response.ok) throw new Error("복습 기록을 불러오지 못했습니다.");
  return response.json();
}

export type ReviewSubmission = {
  job_id?: string;
  session_id: string;
  topic: string;
  transcript_raw: string;
  transcript_corrected: string;
  term_db_used?: {
    safe?: string[];
    content_word_collision?: string[];
    particle_collision?: string[];
  };
};

export type ReviewReport = {
  review_id: string;
  session_id: string;
  score: number;
  transcript: string;
  corrected_transcript: string;
  quantitative: {
    concept_recall: number;
    concept_precision: number;
    concept_f1: number;
    scores: {
      accuracy: ScoreDetail;
      coverage: ScoreDetail;
      structural_understanding: ScoreDetail;
    };
    total: ScoreDetail;
  };
  qualitative: {
    missing_concepts: string[];
    incorrect_concepts: string[];
    misconnected_concepts: string[];
    review_suggestions: string[];
  };
  status: string;
};

type ScoreDetail = {
  score: number;
  max_score: number;
  rubric_level: number;
  reason: string;
};

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
