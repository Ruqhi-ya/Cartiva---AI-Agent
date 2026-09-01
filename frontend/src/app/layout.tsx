import type { Metadata } from "next";

import { NavBar } from "@/components/NavBar";
import { CartProvider } from "@/lib/CartContext";
import "./globals.css";

export const metadata: Metadata = {
  title: "Cartiva — AI-powered shopping that builds a better cart",
  description:
    "Cartiva is an embeddable AI shopping assistant that understands your intent, optimizes your cart, and builds dynamic product bundles.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <CartProvider>
          <NavBar />
          <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
        </CartProvider>
      </body>
    </html>
  );
}
