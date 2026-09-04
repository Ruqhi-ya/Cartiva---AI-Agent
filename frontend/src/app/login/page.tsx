"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { api, ApiError } from "@/lib/api";

export default function LoginPage() {
  const [mode, setMode] = useState<"login" | "signup">("login");

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      if (mode === "signup") {
        await api.signup({
          name,
          email,
          password,
        });

        setSuccess("Account created successfully. Welcome to Cartiva!");

        setTimeout(() => {
          window.location.href = "/cartiva-ai";
        }, 700);
      } else {
        await api.login({
          email,
          password,
        });

        setSuccess("Login successful. Welcome back!");

        setTimeout(() => {
          window.location.href = "/cartiva-ai";
        }, 700);
      }
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-[75vh] items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        {/* Brand */}
        <div className="mb-8 text-center">
          <Link
            href="/"
            className="text-2xl font-extrabold tracking-tight text-ink"
          >
            Cartiva
          </Link>

          <p className="mt-2 text-sm text-muted">
            Your AI-powered shopping companion.
          </p>
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-line bg-card p-6 shadow-soft sm:p-8">
          {/* Tabs */}
          <div className="mb-6 grid grid-cols-2 rounded-xl bg-page p-1">
            <button
              type="button"
              onClick={() => {
                setMode("login");
                setError("");
                setSuccess("");
              }}
              className={`rounded-lg px-4 py-2.5 text-sm font-semibold transition ${
                mode === "login"
                  ? "bg-card text-ink shadow-sm"
                  : "text-muted"
              }`}
            >
              Log in
            </button>

            <button
              type="button"
              onClick={() => {
                setMode("signup");
                setError("");
                setSuccess("");
              }}
              className={`rounded-lg px-4 py-2.5 text-sm font-semibold transition ${
                mode === "signup"
                  ? "bg-card text-ink shadow-sm"
                  : "text-muted"
              }`}
            >
              Create account
            </button>
          </div>

          {/* Heading */}
          <div className="mb-6">
            <h1 className="text-xl font-extrabold text-ink">
              {mode === "login"
                ? "Welcome back"
                : "Create your Cartiva account"}
            </h1>

            <p className="mt-1 text-sm text-muted">
              {mode === "login"
                ? "Log in to continue shopping with Cartiva AI."
                : "Create an account to unlock your personalized AI shopping experience."}
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === "signup" && (
              <div>
                <label className="mb-1.5 block text-sm font-medium text-ink">
                  Name
                </label>

                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  required
                  className="w-full rounded-xl border border-line bg-page px-4 py-3 text-sm outline-none transition focus:border-primary"
                />
              </div>
            )}

            <div>
              <label className="mb-1.5 block text-sm font-medium text-ink">
                Email
              </label>

              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                className="w-full rounded-xl border border-line bg-page px-4 py-3 text-sm outline-none transition focus:border-primary"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-ink">
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 8 characters"
                required
                minLength={8}
                className="w-full rounded-xl border border-line bg-page px-4 py-3 text-sm outline-none transition focus:border-primary"
              />
            </div>

            {/* Error */}
            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            {/* Success */}
            {success && (
              <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
                {success}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white transition hover:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading
                ? "Please wait..."
                : mode === "login"
                  ? "Log in to Cartiva"
                  : "Create Cartiva account"}
            </button>
          </form>

          {/* Store link */}
          <div className="mt-6 text-center">
            <Link
              href="/"
              className="text-sm text-muted hover:text-ink"
            >
              ← Continue browsing the store
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}