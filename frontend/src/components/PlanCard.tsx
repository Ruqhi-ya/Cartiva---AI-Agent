"use client";

interface Props {
  name: string;
  price: string;
  features: string[];
  current: boolean;
  highlight?: boolean;
  ctaLabel: string;
  onSelect?: () => void;
  busy?: boolean;
  disabled?: boolean;
}

export function PlanCard({
  name,
  price,
  features,
  current,
  highlight,
  ctaLabel,
  onSelect,
  busy,
  disabled,
}: Props) {
  return (
    <div
      className={`flex flex-col rounded-2xl border bg-card p-5 shadow-soft ${
        highlight ? "border-primary ring-1 ring-primary/30" : "border-line"
      }`}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-ink">{name}</h3>
        {current && (
          <span className="rounded-full bg-success/10 px-2.5 py-0.5 text-xs font-semibold text-success">
            Current plan
          </span>
        )}
      </div>
      <p className="mt-1 text-2xl font-extrabold text-ink">{price}</p>

      <ul className="mt-4 flex-1 space-y-2 text-sm text-muted">
        {features.map((f) => (
          <li key={f} className="flex items-start gap-2">
            <span className="mt-0.5 text-primary">✓</span>
            <span>{f}</span>
          </li>
        ))}
      </ul>

      <button
        onClick={onSelect}
        disabled={disabled || busy}
        className={`mt-5 w-full rounded-xl py-2.5 text-sm font-semibold transition ${
          disabled
            ? "cursor-not-allowed bg-line text-muted"
            : highlight
            ? "bg-primary text-white hover:bg-primary-dark"
            : "border border-line bg-card text-ink hover:border-primary/40"
        }`}
      >
        {busy ? "Processing…" : ctaLabel}
      </button>
    </div>
  );
}
