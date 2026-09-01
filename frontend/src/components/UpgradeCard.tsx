"use client";

import Link from "next/link";

// Shown inside Cartiva AI when the free usage limit is reached.
export function UpgradeCard() {
  return (
    <div className="rounded-2xl border border-primary/30 bg-primary/5 p-4">
      <h3 className="text-sm font-bold text-ink">
        You've reached your free Cartiva limit
      </h3>
      <p className="mt-1 text-xs text-muted">
        Upgrade to Cartiva Plus for continued AI shopping, advanced bundle
        building, and smarter cart optimization.
      </p>
      <Link
        href="/plus"
        className="mt-3 inline-flex rounded-lg bg-primary px-4 py-2 text-xs font-semibold text-white hover:bg-primary-dark"
      >
        Upgrade to Cartiva Plus
      </Link>
    </div>
  );
}
