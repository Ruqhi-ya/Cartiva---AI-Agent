// Thin API client for the Cartiva backend.
// All secrets stay on the backend; the frontend only knows the base URL.
import type {
  Bundle,
  Cart,
  ChatResponse,
  Product,
  Recommendation,
  Subscription,
  Usage,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** Error whose message is safe to display to users. */
export class ApiError extends Error {}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
      ...init,
    });
  } catch {
    throw new ApiError("We couldn't reach Cartiva. Please check your connection.");
  }

  if (!res.ok) {
    let message = "Something went wrong. Please try again.";
    try {
      const body = await res.json();
      if (body?.detail) message = body.detail;
    } catch {
      /* keep default */
    }
    throw new ApiError(message);
  }
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}

export const api = {
  // Products
  listProducts: (params: { q?: string; category?: string } = {}) => {
    const qs = new URLSearchParams();
    if (params.q) qs.set("q", params.q);
    if (params.category) qs.set("category", params.category);
    const suffix = qs.toString() ? `?${qs}` : "";
    return request<Product[]>(`/api/products${suffix}`);
  },
  categories: () => request<string[]>(`/api/products/categories`),
  getProduct: (id: number) => request<Product>(`/api/products/${id}`),

  // Cart
  getCart: () => request<Cart>(`/api/cart`),
  addToCart: (product_id: number, quantity = 1) =>
    request<Cart>(`/api/cart/items`, {
      method: "POST",
      body: JSON.stringify({ product_id, quantity }),
    }),
  removeFromCart: (itemId: number) =>
    request<Cart>(`/api/cart/items/${itemId}`, { method: "DELETE" }),

  // Agent
  chat: (message: string) =>
    request<ChatResponse>(`/api/agent/chat`, {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
  recommend: (product_id?: number) =>
    request<Recommendation[]>(`/api/agent/recommend`, {
      method: "POST",
      body: JSON.stringify({ product_id: product_id ?? null }),
    }),
  bundle: (goal: string, budget?: number | null) =>
    request<Bundle>(`/api/agent/bundle`, {
      method: "POST",
      body: JSON.stringify({ goal, budget: budget ?? null }),
    }),

  // Usage + subscription
usage: () => request<Usage>(`/api/usage`),

subscription: () =>
  request<Subscription>(`/api/subscription`),

upgrade: (plan: "free" | "plus") =>
  request<Subscription>(`/api/subscription/upgrade`, {
    method: "POST",
    body: JSON.stringify({ plan }),
  }),

createSubscriptionOrder: () =>
  request<{
    order_id: string;
    amount: number;
    currency: string;
    key_id: string;
  }>(`/api/subscription/create-order`, {
    method: "POST",
  }),

verifySubscriptionPayment: (data: {
  razorpay_payment_id: string;
  razorpay_order_id: string;
  razorpay_signature: string;
}) =>
  request<Subscription>(`/api/subscription/verify-payment`, {
    method: "POST",
    body: JSON.stringify(data),
  }),
};

export const formatINR = (value: number) =>
  `₹${Math.round(value).toLocaleString("en-IN")}`;
