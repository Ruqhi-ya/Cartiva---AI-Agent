"use client";

// Global cart + usage state shared across all screens.
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { api, ApiError } from "./api";
import type { Cart, Usage } from "./types";

interface CartContextValue {
  cart: Cart | null;
  usage: Usage | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  refreshUsage: () => Promise<void>;
  addToCart: (productId: number, quantity?: number) => Promise<void>;
  removeFromCart: (itemId: number) => Promise<void>;
  setUsage: (u: Usage) => void;
}

const CartContext = createContext<CartContextValue | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const [cart, setCart] = useState<Cart | null>(null);
  const [usage, setUsage] = useState<Usage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [c, u] = await Promise.all([api.getCart(), api.usage()]);
      setCart(c);
      setUsage(u);
      setError(null);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Unable to load your cart.");
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshUsage = useCallback(async () => {
    try {
      setUsage(await api.usage());
    } catch {
      /* non-critical */
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const addToCart = useCallback(async (productId: number, quantity = 1) => {
    const updated = await api.addToCart(productId, quantity);
    setCart(updated);
  }, []);

  const removeFromCart = useCallback(async (itemId: number) => {
    const updated = await api.removeFromCart(itemId);
    setCart(updated);
  }, []);

  return (
    <CartContext.Provider
      value={{
        cart,
        usage,
        loading,
        error,
        refresh,
        refreshUsage,
        addToCart,
        removeFromCart,
        setUsage,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}
