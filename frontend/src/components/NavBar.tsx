"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useCart } from "@/lib/CartContext";
import { Logo } from "./Logo";
import { UsageIndicator } from "./UsageIndicator";

const links = [
  { href: "/", label: "Store" },
  { href: "/cartiva-ai", label: "Cartiva AI" },
  { href: "/cart", label: "Cart" },
  { href: "/plus", label: "Cartiva Plus" },
];

export function NavBar() {
  const pathname = usePathname();
  const { cart, usage } = useCart();
  const count = cart?.item_count ?? 0;

  return (
    <header className="sticky top-0 z-30 border-b border-line bg-card/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3">
        <Link href="/" aria-label="Cartiva home">
          <Logo />
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {links.map((l) => {
            const active = pathname === l.href;
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                  active
                    ? "bg-primary/10 text-primary"
                    : "text-muted hover:text-ink"
                }`}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-3">
          <div className="hidden sm:block">
            <UsageIndicator usage={usage} />
          </div>
          <Link
            href="/cart"
            className="relative rounded-lg border border-line bg-card px-3 py-1.5 text-sm font-medium text-ink hover:border-primary/40"
          >
            Cart
            {count > 0 && (
              <span className="absolute -right-2 -top-2 flex h-5 min-w-5 items-center justify-center rounded-full bg-primary px-1 text-[11px] font-bold text-white">
                {count}
              </span>
            )}
          </Link>
        </div>
      </div>

      {/* Mobile nav */}
      <nav className="flex items-center gap-1 overflow-x-auto border-t border-line px-4 py-2 md:hidden">
        {links.map((l) => {
          const active = pathname === l.href;
          return (
            <Link
              key={l.href}
              href={l.href}
              className={`whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium ${
                active ? "bg-primary/10 text-primary" : "text-muted"
              }`}
            >
              {l.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
