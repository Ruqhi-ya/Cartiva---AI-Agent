"use client";

import Image from "next/image";
import { useState } from "react";

import { formatINR } from "@/lib/api";
import type { Bundle } from "@/lib/types";

interface Props {
  bundle: Bundle;
  onAddBundle: (bundle: Bundle) => Promise<void>;
  onMakeCheaper: () => Promise<void>;
  onChangeProducts: () => void;
}

// Dynamic bundle presented by Cartiva AI. Customer approves before adding.
export function BundleCard({
  bundle,
  onAddBundle,
  onMakeCheaper,
  onChangeProducts,
}: Props) {
  const [busy, setBusy] = useState<"add" | "cheaper" | null>(null);
  const [added, setAdded] = useState(false);

  const run = async (kind: "add" | "cheaper", fn: () => Promise<void>) => {
    setBusy(kind);
    try {
      await fn();
      if (kind === "add") setAdded(true);
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="overflow-hidden rounded-2xl border border-line bg-card shadow-soft">
      <div className="flex items-center justify-between border-b border-line px-4 py-3">
        <div>
          <h3 className="text-sm font-bold text-ink">{bundle.title}</h3>
          <p className="text-xs text-muted">{bundle.items.length} products</p>
        </div>
        <div className="text-right">
          <div className="text-lg font-extrabold text-ink">
            {formatINR(bundle.total)}
          </div>
          {bundle.budget != null && (
            <span
              className={`text-[11px] font-semibold ${
                bundle.within_budget ? "text-success" : "text-amber-600"
              }`}
            >
              {bundle.within_budget
                ? `Within ₹${Math.round(bundle.budget)}`
                : `Over ₹${Math.round(bundle.budget)}`}
            </span>
          )}
        </div>
      </div>

      <ul className="divide-y divide-line">
        {bundle.items.map(({ product }) => (
          <li key={product.id} className="flex items-center gap-3 px-4 py-2.5">
            <div className="relative h-10 w-10 shrink-0 overflow-hidden rounded-lg bg-bg">
              <Image
                src={product.image}
                alt={product.name}
                fill
                sizes="40px"
                className="object-cover"
              />
            </div>
            <span className="flex-1 truncate text-sm text-ink">{product.name}</span>
            <span className="text-sm font-semibold text-ink">
              {formatINR(product.price)}
            </span>
          </li>
        ))}
      </ul>

      <p className="border-t border-line bg-bg/50 px-4 py-2.5 text-xs text-muted">
        {bundle.explanation}
      </p>

      <div className="flex flex-wrap gap-2 border-t border-line p-3">
        <button
          onClick={() => run("add", () => onAddBundle(bundle))}
          disabled={busy !== null || added}
          className={`rounded-lg px-3 py-2 text-xs font-semibold transition ${
            added
              ? "bg-success text-white"
              : "bg-primary text-white hover:bg-primary-dark"
          }`}
        >
          {added ? "Added to Cart ✓" : busy === "add" ? "Adding…" : "Add Bundle to Cart"}
        </button>
        <button
          onClick={() => run("cheaper", onMakeCheaper)}
          disabled={busy !== null}
          className="rounded-lg border border-line bg-card px-3 py-2 text-xs font-semibold text-ink hover:border-primary/40"
        >
          {busy === "cheaper" ? "Optimizing…" : "Make It Cheaper"}
        </button>
        <button
          onClick={onChangeProducts}
          disabled={busy !== null}
          className="rounded-lg border border-line bg-card px-3 py-2 text-xs font-semibold text-ink hover:border-primary/40"
        >
          Change Products
        </button>
      </div>
    </div>
  );
}
