"use client";

import Script from "next/script";
import { useState } from "react";

import { Banner } from "@/components/Banner";
import { PlanCard } from "@/components/PlanCard";
import { api, ApiError } from "@/lib/api";
import { useCart } from "@/lib/CartContext";

export default function PlusPage() {
  const { usage, refreshUsage, setUsage } = useCart();

  const [busy, setBusy] = useState<"free" | "plus" | null>(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  const plan = usage?.plan ?? "free";

  const upgradeToPlus = async () => {
    setBusy("plus");
    setNotice("");
    setError("");

    try {
      // 1. Ask backend to create a Razorpay order.
      const order = await api.createSubscriptionOrder();

      // 2. Make sure Razorpay Checkout is loaded.
      if (!window.Razorpay) {
        throw new ApiError(
          "Payment checkout is still loading. Please try again."
        );
      }

      // 3. Open Razorpay Checkout.
      const options: RazorpayOptions = {
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: "Cartiva AI",
        description: "Cartiva Plus - Monthly Subscription",
        order_id: order.order_id,

        // 4. Razorpay calls this after successful payment.
        handler: async (response) => {
          try {
            setNotice("Payment received. Verifying your payment...");

            // 5. Send payment details to our backend.
            const subscription =
              await api.verifySubscriptionPayment({
                razorpay_payment_id:
                  response.razorpay_payment_id,
                razorpay_order_id:
                  response.razorpay_order_id,
                razorpay_signature:
                  response.razorpay_signature,
              });

            // 6. Refresh usage/plan information.
            const fresh = await api.usage();
            setUsage(fresh);
            await refreshUsage();

            if (subscription.plan === "plus") {
              setNotice(
                "🎉 You're now on Cartiva Plus! Enjoy unlimited AI shopping."
              );
            } else {
              setNotice(
                "Payment was received, but your Plus plan could not be activated."
              );
            }
          } catch (e) {
            setError(
              e instanceof ApiError
                ? e.message
                : "Payment verification failed. Please contact support."
            );
          } finally {
            setBusy(null);
          }
        },

        modal: {
          ondismiss: () => {
            setNotice("Payment cancelled.");
            setBusy(null);
          },
        },

        theme: {
          color: "#7c3aed",
        },
      };

      const razorpay = new window.Razorpay(options);

      razorpay.open();
    } catch (e) {
      setError(
        e instanceof ApiError
          ? e.message
          : "Couldn't start the payment. Please try again."
      );

      setBusy(null);
    }
  };

  const changePlan = async (target: "free" | "plus") => {
    if (target === "plus") {
      await upgradeToPlus();
      return;
    }

    setBusy("free");
    setNotice("");
    setError("");

    try {
      await api.upgrade("free");

      const fresh = await api.usage();
      setUsage(fresh);
      await refreshUsage();

      setNotice("You've switched back to the Free plan.");
    } catch (e) {
      setError(
        e instanceof ApiError
          ? e.message
          : "Couldn't update your plan."
      );
    } finally {
      setBusy(null);
    }
  };

  return (
    <>
      {/* Razorpay Checkout script */}
      <Script
        src="https://checkout.razorpay.com/v1/checkout.js"
        strategy="afterInteractive"
      />

      <div className="space-y-6">
        <div>
          <h1 className="text-xl font-extrabold text-ink">
            Cartiva Plus
          </h1>

          <p className="text-sm text-muted">
            Unlock unlimited AI shopping and advanced tools.
          </p>
        </div>

        {/* Current plan + usage */}
        <div className="flex flex-col gap-3 rounded-2xl border border-line bg-card p-4 shadow-soft sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-muted">
              Current plan
            </p>

            <p className="text-lg font-bold text-ink">
              {plan === "plus"
                ? "Cartiva Plus"
                : "Cartiva Free"}
            </p>
          </div>

          <div className="text-sm text-muted">
            {usage?.plan === "plus" ||
            usage?.limit === null ? (
              <span className="font-semibold text-primary">
                Unlimited AI sessions
              </span>
            ) : (
              <span>
                <span className="font-semibold text-ink">
                  {usage?.remaining ?? 0}
                </span>{" "}
                of {usage?.limit ?? 0} AI sessions
                remaining this {usage?.reset_period}
              </span>
            )}
          </div>
        </div>

        <Banner message={error} />
        <Banner message={notice} tone="info" />

        <div className="grid gap-4 md:grid-cols-2">
          <PlanCard
            name="Cartiva Free"
            price="₹0"
            current={plan === "free"}
            ctaLabel={
              plan === "free"
                ? "Current plan"
                : "Switch to Free"
            }
            disabled={plan === "free"}
            busy={busy === "free"}
            onSelect={() => changePlan("free")}
            features={[
              "Limited AI shopping sessions",
              "Smart cart recommendations",
              "Dynamic bundle builder",
            ]}
          />

          <PlanCard
            name="Cartiva Plus"
            price="₹499 / month"
            highlight
            current={plan === "plus"}
            ctaLabel={
              plan === "plus"
                ? "Current plan"
                : "Upgrade to Plus"
            }
            disabled={plan === "plus"}
            busy={busy === "plus"}
            onSelect={() => changePlan("plus")}
            features={[
              "Unlimited AI shopping sessions",
              "Advanced bundle building",
              "Advanced cart optimization",
              "Priority AI responses",
            ]}
          />
        </div>

        <p className="text-center text-xs text-muted">
          Payments are processed securely through Razorpay Test Mode.
          You will complete the payment yourself.
        </p>
      </div>
    </>
  );
}