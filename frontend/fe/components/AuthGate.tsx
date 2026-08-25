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
    <main className="grid min-h-screen place-items-center bg-slate-950 px-6 text-white">
      <section className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-8">
        <p className="text-sm font-semibold text-cyan-300">YBIGTA 29th - AI 구술 복습 서비스</p>
        <h1 className="mt-5 text-3xl font-bold leading-tight">힘빼지 말고,<br />우리 말로 하자.</h1>
        <p className="mt-4 text-sm leading-6 text-slate-400">로그인해서 복습을 시작해보세요.</p>
        {message && <p className="mt-5 rounded-lg border border-rose-400/30 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{message}</p>}
        <button
          type="button"
          onClick={startGoogleLogin}
          disabled={!googleClientId}
          className="mt-8 flex w-full items-center justify-center gap-3 rounded-lg bg-white px-4 py-3 font-semibold text-slate-900 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <span className="grid h-6 w-6 place-items-center rounded-full border border-slate-300 text-xs font-black">G</span>
          {googleClientId ? "Google로 로그인" : "Google 로그인 설정 필요"}
        </button>
      </section>
    </main>
  );
}
