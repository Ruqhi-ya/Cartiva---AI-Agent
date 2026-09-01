import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#F8F9FB",
        primary: "#5B5FEF",
        "primary-dark": "#4548C8",
        ink: "#17181C",
        muted: "#6B7280",
        card: "#FFFFFF",
        line: "#E5E7EB",
        success: "#16A34A",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 1px 3px rgba(23,24,28,0.06), 0 8px 24px rgba(23,24,28,0.05)",
      },
      borderRadius: {
        xl: "0.9rem",
        "2xl": "1.25rem",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "typing": {
          "0%, 60%, 100%": { opacity: "0.3" },
          "30%": { opacity: "1" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.25s ease-out",
        "typing": "typing 1.2s infinite ease-in-out",
      },
    },
  },
  plugins: [],
};

export default config;
