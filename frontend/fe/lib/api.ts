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
  feedback: {
    summary: string;
    strengths: string[];
    missing_points: string[];
    suggestions: string[];
  };
  status: string;
  metrics?: {
    corrected_cer?: number;
    corrected_precision?: number;
    corrected_recall?: number;
    corrected_f1?: number;
  };
  breakdown?: {
    fidelity: number;
    connectivity: number;
    comprehensiveness: number;
  };
};

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
