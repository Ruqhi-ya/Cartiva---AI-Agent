import type { Usage } from "@/lib/types";

// Compact pill showing remaining AI usage / plan.
export function UsageIndicator({ usage }: { usage: Usage | null }) {
  if (!usage) return null;

  if (usage.plan === "plus" || usage.limit === null) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
        ✦ Cartiva Plus · Unlimited
      </span>
    );
  }

  const low = (usage.remaining ?? 0) <= 2;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${
        low ? "bg-amber-100 text-amber-700" : "bg-line/60 text-muted"
      }`}
      title={`Resets ${usage.reset_period}`}
    >
      {usage.remaining} / {usage.limit} AI sessions left
    </span>
  );
}
