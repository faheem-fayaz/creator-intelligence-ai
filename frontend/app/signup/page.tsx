"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authRequest, getToken, saveAuth } from "@/lib/auth";

export default function SignupPage() {
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

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      setLoading(false);
      return;
    }

    if (true && password !== String(form.get("confirmPassword") || "")) {
      setError("Passwords do not match.");
      setLoading(false);
      return;
    }

    try {
      const data = await authRequest("/auth/signup", {
        name: String(form.get('name') || ''),
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
          <h1 className="mt-6 text-3xl font-bold">{"Create your account"}</h1>
          <p className="mt-2 text-zinc-400">{"Create an account to use Creator AI."}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">

          <div>
            <label className="mb-2 block text-sm text-zinc-400">Name</label>
            <input
              name="name"
              required
              minLength={2}
              placeholder="Your name"
              className="auth-input"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm text-zinc-400">Email</label>
            <input name="email" type="email" required placeholder="you@example.com" className="auth-input" />
          </div>

          <div>
            <label className="mb-2 block text-sm text-zinc-400">Password</label>
            <input name="password" type="password" required placeholder="At least 8 characters" className="auth-input" />
          </div>
          <div>
            <label className="mb-2 block text-sm text-zinc-400">Confirm password</label>
            <input name="confirmPassword" type="password" required placeholder="Repeat your password" className="auth-input" />
          </div>
          {error && <p className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</p>}

          <button type="submit" disabled={loading} className="auth-button">
            {loading ? "Please wait..." : "Create account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-zinc-500">
          Already have an account? 
          <Link href="/login" className="auth-link">
            Log in
          </Link>
        </p>
      </section>
    </main>
  );
}
