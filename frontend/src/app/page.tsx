"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Banner } from "@/components/Banner";
import { ProductCard } from "@/components/ProductCard";
import { api, ApiError } from "@/lib/api";
import { useCart } from "@/lib/CartContext";
import type { Product } from "@/lib/types";

export default function StorePage() {
  const { addToCart } = useCart();
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [activeCat, setActiveCat] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async (q: string, cat: string | null) => {
    setLoading(true);

    try {
      const list = await api.listProducts({
        q: q || undefined,
        category: cat || undefined,
      });

      setProducts(list);
      setError("");
    } catch (e) {
      setError(
        e instanceof ApiError
          ? e.message
          : "Unable to load products."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    api
      .categories()
      .then(setCategories)
      .catch(() => setCategories([]));

    load("", null);
  }, [load]);

  const onSearch = (e: React.FormEvent) => {
    e.preventDefault();
    load(query, activeCat);
  };

  const selectCat = (cat: string | null) => {
    setActiveCat(cat);
    load(query, cat);
  };

  return (
    <div className="space-y-6">

      {/* Connected Demo Store */}
      <div className="flex flex-col gap-4 rounded-2xl border border-line bg-card p-5 shadow-soft sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-line bg-page px-3 py-1 text-xs font-semibold text-muted">
            <span className="h-2 w-2 rounded-full bg-primary" />
            Connected Demo Store
          </div>

          <h1 className="text-xl font-extrabold text-ink">
            Cartiva Demo Store
          </h1>

          <p className="mt-1 text-sm text-muted">
            A reference shopping environment powered by Cartiva AI.
          </p>
        </div>

        <Link
          href="/cartiva-ai"
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-dark"
        >
          ✦ Ask Cartiva AI
        </Link>
      </div>

      {/* Search + categories */}
      <div className="space-y-3">
        <form onSubmit={onSearch} className="flex gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search products…"
            className="flex-1 rounded-xl border border-line bg-card px-4 py-2.5 text-sm outline-none focus:border-primary"
          />

          <button
            type="submit"
            className="rounded-xl bg-ink px-4 py-2.5 text-sm font-semibold text-white"
          >
            Search
          </button>
        </form>

        <div className="flex flex-wrap gap-2">
          <CategoryPill
            label="All"
            active={!activeCat}
            onClick={() => selectCat(null)}
          />

          {categories.map((c) => (
            <CategoryPill
              key={c}
              label={c}
              active={activeCat === c}
              onClick={() => selectCat(c)}
            />
          ))}
        </div>
      </div>

      <Banner message={error} />

      {/* Products */}
      {loading ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={i}
              className="aspect-[3/4] animate-pulse rounded-2xl border border-line bg-card"
            />
          ))}
        </div>
      ) : products.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted">
          No products found. Try a different search or category.
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {products.map((p) => (
            <ProductCard
              key={p.id}
              product={p}
              onAdd={(prod) => addToCart(prod.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function CategoryPill({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full border px-3.5 py-1.5 text-sm font-medium transition ${
        active
          ? "border-primary bg-primary text-white"
          : "border-line bg-card text-muted hover:border-primary/40"
      }`}
    >
      {label}
    </button>
  );
}