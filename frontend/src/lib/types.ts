// Shared types mirroring the backend API responses.

export interface Product {
  id: number;
  name: string;
  description: string;
  category: string;
  price: number;
  image: string;
  stock: number;
  tags: string[];
  is_premium: boolean;
}

export interface CartItem {
  id: number;
  product: Product;
  quantity: number;
  line_total: number;
}

export interface Cart {
  id: number;
  items: CartItem[];
  subtotal: number;
  total: number;
  item_count: number;
}

export interface Recommendation {
  product: Product;
  reason: string;
  kind: "cross_sell" | "upsell";
}

export interface Bundle {
  title: string;
  items: { product: Product }[];
  total: number;
  budget: number | null;
  within_budget: boolean;
  explanation: string;
}

export interface Usage {
  plan: string;
  limit: number | null;
  used: number;
  remaining: number | null;
  period: string;
  reset_period: string;
  limit_reached: boolean;
}

export interface Subscription {
  plan: string;
  status: string;
}

export interface ChatResponse {
  reply: string;
  intent: string;
  recommendations: Recommendation[];
  bundle: Bundle | null;
  usage: Usage;
}
