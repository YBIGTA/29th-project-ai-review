const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export type ReviewSubmission = {
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

export async function transcribeAudio(audio: Blob, sessionId: string, topic: string): Promise<TranscriptionResult> {
  const formData = new FormData();
  formData.append("session_id", sessionId);
  formData.append("topic", topic);
  formData.append("audio_file", audio, "review.webm");
  const endpoint = API_BASE_URL ? `${API_BASE_URL}/api/stt/transcribe` : "/api/stt/transcribe";
  const response = await fetch(endpoint, { method: "POST", body: formData });
  if (!response.ok) throw new Error((await response.text()) || "STT request failed");
  return response.json();
}

export async function submitReview(payload: ReviewSubmission): Promise<ReviewReport> {
  const endpoint = API_BASE_URL ? `${API_BASE_URL}/api/reviews/submit` : "/api/reviews/submit";
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Review submission failed");
  }

  return response.json();
}
