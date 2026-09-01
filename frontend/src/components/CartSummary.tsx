import { formatINR } from "@/lib/api";
import type { Cart } from "@/lib/types";

interface Props {
  cart: Cart;
  onCheckout: () => void;
}

export function CartSummary({ cart, onCheckout }: Props) {
  const empty = cart.item_count === 0;
  return (
    <div className="rounded-2xl border border-line bg-card p-4 shadow-soft">
      <h3 className="text-sm font-bold text-ink">Order Summary</h3>
      <dl className="mt-3 space-y-2 text-sm">
        <div className="flex justify-between text-muted">
          <dt>Subtotal ({cart.item_count} items)</dt>
          <dd className="font-medium text-ink">{formatINR(cart.subtotal)}</dd>
        </div>
        <div className="flex justify-between border-t border-line pt-2 text-base font-bold text-ink">
          <dt>Total</dt>
          <dd>{formatINR(cart.total)}</dd>
        </div>
      </dl>
      <button
        onClick={onCheckout}
        disabled={empty}
        className={`mt-4 w-full rounded-xl py-2.5 text-sm font-semibold transition ${
          empty
            ? "cursor-not-allowed bg-line text-muted"
            : "bg-primary text-white hover:bg-primary-dark"
        }`}
      >
        Continue to Checkout
      </button>
      <p className="mt-2 text-center text-[11px] text-muted">
        You control checkout. Cartiva never purchases on your behalf.
      </p>
    </div>
  );
}
