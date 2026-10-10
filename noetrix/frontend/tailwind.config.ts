import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#F6EFE3",
        cream: "#F6EFE3",
        "card-surface": "#FDFAF4",
        ink: "#0C0F17",
        "ink-slate": "#1D2230",
        "ink-muted": "rgba(12, 15, 23, 0.45)",
        "ink-border": "rgba(12, 15, 23, 0.15)",
        "accent-yellow": "#FAE425",
        "accent-lilac": "#DBACF0",
        "accent-coral": "#FF8465",
        "accent-emerald": "#10B981",
      },
      fontFamily: {
        display: ["Anton", "Impact", "sans-serif"],
        sans: ["DM Sans", "Inter", "sans-serif"],
      },
      borderRadius: {
        pill: "100px",
      },
    },
  },
  plugins: [],
};

export default config;
