"use client";

import { useEffect, useState } from "react";
import ReviewApp from "@/components/ReviewApp";
import { getCurrentUser, type User } from "@/lib/api";

const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

export default function AuthGate() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "로그인 상태를 확인하지 못했습니다."))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return <div className="grid min-h-screen place-items-center bg-slate-950 text-slate-300">로그인 상태를 확인하고 있습니다...</div>;
  }

  if (error) {
    return <LoginScreen message={error} />;
  }

  return user ? <ReviewApp user={user} /> : <LoginScreen />;
}

function LoginScreen({ message }: { message?: string }) {
  const startGoogleLogin = () => {
    if (!googleClientId) return;
    const redirectUri = process.env.NEXT_PUBLIC_GOOGLE_REDIRECT_URI ?? `${window.location.origin}/auth/google/callback`;
    const state = crypto.randomUUID();
    sessionStorage.setItem("google_oauth_state", state);
    const params = new URLSearchParams({
      client_id: googleClientId,
      redirect_uri: redirectUri,
      response_type: "code",
      scope: "openid email profile",
      state,
      access_type: "offline",
    });
    window.location.assign(`https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`);
  };

  return (
    <main className="relative grid min-h-screen place-items-center overflow-hidden bg-slate-950 px-6 text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.16),transparent_38%),radial-gradient(circle_at_bottom_left,rgba(251,191,36,0.12),transparent_35%)]" />
      <section className="relative w-full max-w-md rounded-3xl border border-slate-800 bg-slate-900/90 p-8 shadow-2xl shadow-slate-950/60">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-300">YBIGTA AI REVIEW</p>
        <h1 className="mt-5 text-3xl font-bold leading-tight">말로 설명하고,<br />더 오래 기억하세요.</h1>
        <p className="mt-4 text-sm leading-6 text-slate-400">Google 계정으로 로그인하면 발표 기록과 맞춤형 복습 결과를 안전하게 관리할 수 있습니다.</p>
        {message && <p className="mt-5 rounded-xl border border-rose-400/30 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{message}</p>}
        <button
          type="button"
          onClick={startGoogleLogin}
          disabled={!googleClientId}
          className="mt-8 flex w-full items-center justify-center gap-3 rounded-xl bg-white px-4 py-3 font-semibold text-slate-900 transition hover:bg-cyan-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <span className="grid h-6 w-6 place-items-center rounded-full bg-cyan-400 text-xs font-black">G</span>
          {googleClientId ? "Google로 로그인" : "Google 로그인 설정 필요"}
        </button>
      </section>
    </main>
  );
}