"use client";

import Image from "next/image";
import { useState } from "react";

import { formatINR } from "@/lib/api";
import type { Product } from "@/lib/types";

interface Props {
  product: Product;
  onAdd: (product: Product) => Promise<void> | void;
}

export function ProductCard({ product, onAdd }: Props) {
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);
  const [imageError, setImageError] = useState(false);

  const handleAdd = async () => {
    setAdding(true);

    try {
      await onAdd(product);
      setAdded(true);
      setTimeout(() => setAdded(false), 1500);
    } finally {
      setAdding(false);
    }
  };

  const soldOut = product.stock <= 0;

  return (
    <div className="group flex flex-col overflow-hidden rounded-2xl border border-line bg-card shadow-soft transition hover:-translate-y-0.5 hover:shadow-lg">
      <div className="relative aspect-square overflow-hidden bg-bg">
        {!imageError ? (
          <Image
            src={product.image}
            alt={product.name}
            fill
            sizes="(max-width:768px) 50vw, 25vw"
            className="object-cover transition duration-300 group-hover:scale-105"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-gray-100">
            <span className="text-5xl">🛍️</span>
          </div>
        )}

        {product.is_premium && (
          <span className="absolute left-2 top-2 rounded-full bg-ink/85 px-2 py-0.5 text-[11px] font-semibold text-white">
            Premium
          </span>
        )}
      </div>

      <div className="flex flex-1 flex-col p-3.5">
        <span className="text-[11px] font-medium uppercase tracking-wide text-muted">
          {product.category}
        </span>

        <h3 className="mt-0.5 line-clamp-1 text-sm font-semibold text-ink">
          {product.name}
        </h3>

        <p className="mt-1 line-clamp-2 text-xs text-muted">
          {product.description}
        </p>

        <div className="mt-3 flex items-center justify-between">
          <span className="text-base font-bold text-ink">
            {formatINR(product.price)}
          </span>

          <button
            onClick={handleAdd}
            disabled={adding || soldOut}
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
              soldOut
                ? "cursor-not-allowed bg-line text-muted"
                : added
                ? "bg-success text-white"
                : "bg-primary text-white hover:bg-primary-dark"
            }`}
          >
            {soldOut
              ? "Sold out"
              : added
              ? "Added ✓"
              : adding
              ? "…"
              : "Add to Cart"}
          </button>
        </div>
      </div>
    </div>
  );
}