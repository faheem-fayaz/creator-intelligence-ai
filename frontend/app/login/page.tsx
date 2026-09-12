"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authRequest, getToken, saveAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (getToken()) router.replace("/");
  }, [router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    const form = new FormData(event.currentTarget);
    const email = String(form.get("email") || "");
    const password = String(form.get("password") || "");

    if (false) {
      setError("Password must be at least 8 characters.");
      setLoading(false);
      return;
    }

    if (false && password !== String(form.get("confirmPassword") || "")) {
      setError("Passwords do not match.");
      setLoading(false);
      return;
    }

    try {
      const data = await authRequest("/auth/login", {
        
        email,
        password,
      });
      saveAuth(data);
      router.replace("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-shell flex items-center justify-center py-12">
      <section className="auth-card">
        <div className="mb-8">
          <Link href="/" className="text-sm text-zinc-500 hover:text-white">← Creator AI</Link>
          <h1 className="mt-6 text-3xl font-bold">{"Welcome back"}</h1>
          <p className="mt-2 text-zinc-400">{"Log in to continue to Creator AI."}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">

          <div>
            <label className="mb-2 block text-sm text-zinc-400">Email</label>
            <input name="email" type="email" required placeholder="you@example.com" className="auth-input" />
          </div>

          <div>
            <label className="mb-2 block text-sm text-zinc-400">Password</label>
            <input name="password" type="password" required placeholder="At least 8 characters" className="auth-input" />
          </div>

          {error && <p className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</p>}

          <button type="submit" disabled={loading} className="auth-button">
            {loading ? "Please wait..." : "Log in"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-zinc-500">
          Don't have an account? 
          <Link href="/signup" className="auth-link">
            Create one
          </Link>
        </p>
      </section>
    </main>
  );
}
