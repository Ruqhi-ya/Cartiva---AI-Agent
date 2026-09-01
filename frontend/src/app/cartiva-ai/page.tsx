"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { AIMessage, TypingBubble } from "@/components/AIMessage";
import { BundleCard } from "@/components/BundleCard";
import { ProductRecommendation } from "@/components/ProductRecommendation";
import { UpgradeCard } from "@/components/UpgradeCard";
import { UsageIndicator } from "@/components/UsageIndicator";
import { api, ApiError, formatINR } from "@/lib/api";
import { useCart } from "@/lib/CartContext";
import type { Bundle, Recommendation } from "@/lib/types";

interface Msg {
  id: number;
  role: "user" | "ai";
  text?: string;
  recommendations?: Recommendation[];
  bundle?: Bundle;
  goal?: string; // original goal for Make It Cheaper / Change Products
  isUpgrade?: boolean;
}

const SUGGESTIONS = [
  "I need a beginner gym kit under ₹5,000.",
  "Build me a skincare routine under ₹2,000.",
  "What should I add to my cart?",
  "Show me travel essentials.",
];

export default function CartivaAIPage() {
  const { cart, usage, addToCart, refresh, setUsage } = useCart();
  const [messages, setMessages] = useState<Msg[]>([
    {
      id: 0,
      role: "ai",
      text:
        "Hi, I'm Cartiva AI. Tell me what you're shopping for and I'll build a better cart. Try a goal like “a beginner gym kit under ₹5,000”.",
    },
  ]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const nextId = useRef(1);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, thinking]);

  const push = (m: Omit<Msg, "id">) =>
    setMessages((prev) => [...prev, { ...m, id: nextId.current++ }]);

  const send = async (text: string) => {
    const message = text.trim();
    if (!message || thinking) return;
    setInput("");
    push({ role: "user", text: message });
    setThinking(true);

    try {
      const res = await api.chat(message);
      setUsage(res.usage);
      push({
        role: "ai",
        text: res.reply,
        recommendations: res.recommendations.length ? res.recommendations : undefined,
        bundle: res.bundle ?? undefined,
        goal: message,
      });
    } catch (e) {
      if (e instanceof ApiError && /free cartiva limit/i.test(e.message)) {
        push({ role: "ai", text: e.message, isUpgrade: true });
        // reflect that the limit is reached
        try {
          setUsage(await api.usage());
        } catch {
          /* ignore */
        }
      } else {
        push({
          role: "ai",
          text:
            e instanceof ApiError
              ? e.message
              : "Cartiva is unavailable right now. Please try again.",
        });
      }
    } finally {
      setThinking(false);
    }
  };

  const handleAddRec = async (productId: number) => {
    await addToCart(productId);
  };

  const handleAddBundle = async (bundle: Bundle) => {
    // Customer approved — add each product to the cart.
    for (const { product } of bundle.items) {
      await addToCart(product.id);
    }
  };

  const handleMakeCheaper = async (msg: Msg) => {
    if (!msg.bundle || !msg.goal) return;
    const target = Math.round(msg.bundle.total * 0.85);
    try {
      const cheaper = await api.bundle(msg.goal, target);
      push({
        role: "ai",
        text: `Here's a more affordable version at ${formatINR(cheaper.total)}.`,
        bundle: cheaper,
        goal: msg.goal,
      });
    } catch (e) {
      push({
        role: "ai",
        text: e instanceof ApiError ? e.message : "I couldn't make it cheaper.",
      });
    }
  };

  const handleChangeProducts = (msg: Msg) => {
    if (!msg.goal) return;
    setInput(msg.goal);
  };

  const limitReached = usage?.limit_reached && usage.plan !== "plus";

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr,300px]">
      {/* Conversation */}
      <div className="flex h-[calc(100vh-180px)] min-h-[520px] flex-col overflow-hidden rounded-2xl border border-line bg-card shadow-soft">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-primary text-sm font-extrabold text-white">
              C
            </span>
            <div>
              <h1 className="text-sm font-bold text-ink">Cartiva AI</h1>
              <p className="text-[11px] text-muted">Your AI shopping assistant</p>
            </div>
          </div>
          <UsageIndicator usage={usage} />
        </div>

        <div ref={scrollRef} className="scroll-slim flex-1 space-y-4 overflow-y-auto p-4">
          {messages.map((m) => (
            <AIMessage key={m.id} role={m.role}>
              {m.text && <p className="text-sm leading-relaxed">{m.text}</p>}

              {m.recommendations && (
                <div className="space-y-2">
                  {m.recommendations.map((rec) => (
                    <ProductRecommendation
                      key={rec.product.id}
                      rec={rec}
                      onAdd={handleAddRec}
                    />
                  ))}
                </div>
              )}

              {m.bundle && (
                <BundleCard
                  bundle={m.bundle}
                  onAddBundle={handleAddBundle}
                  onMakeCheaper={() => handleMakeCheaper(m)}
                  onChangeProducts={() => handleChangeProducts(m)}
                />
              )}

              {m.isUpgrade && <UpgradeCard />}
            </AIMessage>
          ))}

          {thinking && <TypingBubble />}
        </div>

        {/* Composer */}
        <div className="border-t border-line p-3">
          {limitReached ? (
            <div className="rounded-xl bg-primary/5 p-3 text-center text-sm text-muted">
              You've used all your free AI sessions.{" "}
              <Link href="/plus" className="font-semibold text-primary">
                Upgrade to Cartiva Plus
              </Link>
            </div>
          ) : (
            <>
              <div className="mb-2 flex flex-wrap gap-1.5">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    disabled={thinking}
                    className="rounded-full border border-line bg-bg px-2.5 py-1 text-[11px] text-muted hover:border-primary/40 hover:text-ink"
                  >
                    {s}
                  </button>
                ))}
              </div>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  send(input);
                }}
                className="flex gap-2"
              >
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask Cartiva to build a cart…"
                  className="flex-1 rounded-xl border border-line bg-card px-4 py-2.5 text-sm outline-none focus:border-primary"
                />
                <button
                  type="submit"
                  disabled={thinking || !input.trim()}
                  className="rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-dark disabled:opacity-50"
                >
                  Send
                </button>
              </form>
            </>
          )}
        </div>
      </div>

      {/* Cart summary rail */}
      <aside className="space-y-3">
        <div className="rounded-2xl border border-line bg-card p-4 shadow-soft">
          <h2 className="text-sm font-bold text-ink">Your cart</h2>
          {cart && cart.items.length > 0 ? (
            <>
              <ul className="mt-3 space-y-2">
                {cart.items.map((it) => (
                  <li key={it.id} className="flex justify-between text-sm">
                    <span className="truncate text-muted">
                      {it.quantity}× {it.product.name}
                    </span>
                    <span className="font-medium text-ink">
                      {formatINR(it.line_total)}
                    </span>
                  </li>
                ))}
              </ul>
              <div className="mt-3 flex justify-between border-t border-line pt-2 text-sm font-bold text-ink">
                <span>Total</span>
                <span>{formatINR(cart.total)}</span>
              </div>
              <Link
                href="/cart"
                className="mt-3 block rounded-xl bg-primary py-2 text-center text-sm font-semibold text-white hover:bg-primary-dark"
              >
                View Cart
              </Link>
            </>
          ) : (
            <p className="mt-2 text-sm text-muted">
              Your cart is empty. Ask Cartiva to build one.
            </p>
          )}
          <button
            onClick={refresh}
            className="mt-2 w-full text-center text-[11px] text-muted hover:text-ink"
          >
            Refresh
          </button>
        </div>

        <div className="rounded-2xl border border-line bg-card p-4 text-xs text-muted shadow-soft">
          Cartiva only adds products you approve. You always complete checkout
          yourself.
        </div>
      </aside>
    </div>
  );
}
