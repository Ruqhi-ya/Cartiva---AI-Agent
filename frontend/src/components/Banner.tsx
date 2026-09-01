// Non-intrusive inline banner for user-friendly error / info states.
export function Banner({
  message,
  tone = "error",
}: {
  message: string;
  tone?: "error" | "info";
}) {
  if (!message) return null;
  const styles =
    tone === "error"
      ? "border-red-200 bg-red-50 text-red-700"
      : "border-primary/20 bg-primary/5 text-primary";
  return (
    <div className={`rounded-xl border px-4 py-2.5 text-sm ${styles}`}>
      {message}
    </div>
  );
}
