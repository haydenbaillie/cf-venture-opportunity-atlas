import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1a2330",
        paper: "#f6f2ea",
        mist: "#e7e1d6",
        accent: "#1f4e5f",
        muted: "#5c6570",
        gold: "#8a6a32",
      },
      fontFamily: {
        serif: ["var(--font-source-serif)", "Georgia", "serif"],
        sans: ["var(--font-ibm-plex)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
