"use client";

import Image from "next/image";
import { useState } from "react";

import { formatINR } from "@/lib/api";
import type { Recommendation } from "@/lib/types";

interface Props {
  rec: Recommendation;
  onAdd: (productId: number) => Promise<void>;
}

// A single recommendation card shown by Cartiva AI or the Smart Cart Optimizer.
export function ProductRecommendation({ rec, onAdd }: Props) {
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);

  const handleAdd = async () => {
    setAdding(true);
    try {
      await onAdd(rec.product.id);
      setAdded(true);
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="flex items-center gap-3 rounded-xl border border-line bg-card p-3">
      <div className="relative h-14 w-14 shrink-0 overflow-hidden rounded-lg bg-bg">
        <Image
          src={rec.product.image}
          alt={rec.product.name}
          fill
          sizes="56px"
          className="object-cover"
        />
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <h4 className="truncate text-sm font-semibold text-ink">
            {rec.product.name}
          </h4>
          <span
            className={`rounded-full px-1.5 py-0.5 text-[10px] font-semibold ${
              rec.kind === "upsell"
                ? "bg-primary/10 text-primary"
                : "bg-line/70 text-muted"
            }`}
          >
            {rec.kind === "upsell" ? "Upgrade" : "Goes well"}
          </span>
        </div>
        <p className="mt-0.5 line-clamp-1 text-xs text-muted">{rec.reason}</p>
        <span className="text-sm font-bold text-ink">
          {formatINR(rec.product.price)}
        </span>
      </div>

      <button
        onClick={handleAdd}
        disabled={adding || added}
        className={`shrink-0 rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
          added
            ? "bg-success text-white"
            : "bg-primary text-white hover:bg-primary-dark"
        }`}
      >
        {added ? "Added ✓" : adding ? "…" : "Add"}
      </button>
    </div>
  );
}
