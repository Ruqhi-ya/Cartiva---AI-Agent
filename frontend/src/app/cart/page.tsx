"use client";

import Image from "next/image";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Banner } from "@/components/Banner";
import { CartSummary } from "@/components/CartSummary";
import { ProductRecommendation } from "@/components/ProductRecommendation";
import { api, formatINR } from "@/lib/api";
import { useCart } from "@/lib/CartContext";
import type { Recommendation } from "@/lib/types";

export default function CartPage() {
  const { cart, loading, addToCart, removeFromCart } = useCart();
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [notice, setNotice] = useState("");

  const loadRecs = useCallback(async () => {
    try {
      setRecs(await api.recommend());
    } catch {
      setRecs([]);
    }
  }, []);

  useEffect(() => {
    if (cart && cart.items.length > 0) loadRecs();
    else setRecs([]);
  }, [cart, loadRecs]);

  const handleAddRec = async (productId: number) => {
    await addToCart(productId);
  };

  const handleCheckout = () => {
    // No real payment yet. Razorpay Test Mode will be wired here later.
    setNotice(
      "Checkout is a placeholder in this MVP. Payment (Razorpay) will be added in a later task."
    );
  };

  if (loading) {
    return <p className="py-12 text-center text-sm text-muted">Loading your cart…</p>;
  }

  const empty = !cart || cart.items.length === 0;

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-extrabold text-ink">Your Cart</h1>
      <Banner message={notice} tone="info" />

      {empty ? (
        <div className="rounded-2xl border border-line bg-card p-10 text-center shadow-soft">
          <p className="text-sm text-muted">Your cart is empty.</p>
          <div className="mt-4 flex justify-center gap-2">
            <Link
              href="/"
              className="rounded-xl border border-line px-4 py-2 text-sm font-semibold text-ink hover:border-primary/40"
            >
              Browse Store
            </Link>
            <Link
              href="/cartiva-ai"
              className="rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-primary-dark"
            >
              Ask Cartiva AI
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid gap-5 lg:grid-cols-[1fr,320px]">
          <div className="space-y-4">
            {/* Cart items */}
            <ul className="space-y-3">
              {cart!.items.map((it) => (
                <li
                  key={it.id}
                  className="flex items-center gap-3 rounded-2xl border border-line bg-card p-3 shadow-soft"
                >
                  <div className="relative h-16 w-16 shrink-0 overflow-hidden rounded-xl bg-bg">
                    <Image
                      src={it.product.image}
                      alt={it.product.name}
                      fill
                      sizes="64px"
                      className="object-cover"
                    />
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="truncate text-sm font-semibold text-ink">
                      {it.product.name}
                    </h3>
                    <p className="text-xs text-muted">
                      Qty {it.quantity} · {formatINR(it.product.price)} each
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-ink">
                      {formatINR(it.line_total)}
                    </div>
                    <button
                      onClick={() => removeFromCart(it.id)}
                      className="mt-1 text-xs font-medium text-muted hover:text-red-600"
                    >
                      Remove
                    </button>
                  </div>
                </li>
              ))}
            </ul>

            {/* Smart Cart Optimizer recommendations */}
            {recs.length > 0 && (
              <div className="rounded-2xl border border-line bg-card p-4 shadow-soft">
                <div className="flex items-center gap-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-primary text-[11px] font-extrabold text-white">
                    C
                  </span>
                  <h2 className="text-sm font-bold text-ink">
                    Recommended by Cartiva
                  </h2>
                </div>
                <p className="mb-3 mt-1 text-xs text-muted">
                  These pair well with what's in your cart. Add any you like.
                </p>
                <div className="space-y-2">
                  {recs.map((rec) => (
                    <ProductRecommendation
                      key={rec.product.id}
                      rec={rec}
                      onAdd={handleAddRec}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="lg:sticky lg:top-24 lg:self-start">
            <CartSummary cart={cart!} onCheckout={handleCheckout} />
          </div>
        </div>
      )}
    </div>
  );
}
