"use client";

import { useEffect, useState } from "react";
import { loginWithGoogle } from "@/lib/api";

export default function GoogleCallbackPage() {
  const [message, setMessage] = useState("Google 로그인 정보를 확인하고 있습니다...");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const returnedState = params.get("state");
    const savedState = sessionStorage.getItem("google_oauth_state");
    const redirectUri = process.env.NEXT_PUBLIC_GOOGLE_REDIRECT_URI ?? `${window.location.origin}/auth/google/callback`;

    if (!code || !returnedState || returnedState !== savedState) {
      setMessage("로그인 요청이 유효하지 않습니다. 다시 시도해 주세요.");
      return;
    }

    loginWithGoogle(code, redirectUri)
      .then(() => {
        sessionStorage.removeItem("google_oauth_state");
        window.location.replace("/");
      })
      .catch((reason: unknown) => setMessage(reason instanceof Error ? reason.message : "Google 로그인에 실패했습니다."));
  }, []);

  return <main className="grid min-h-screen place-items-center bg-slate-950 px-6 text-center text-slate-300"><p>{message}</p></main>;
}