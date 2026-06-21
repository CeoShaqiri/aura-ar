import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      colors: {
        // The Aura Standard palette
        plum: "#071526", // deepest — page background
        wine: "#5A6B8C", // steel blue — card surfaces
        mocha: "#5A6B8C", // steel blue — secondary accents
        rose: "#F28D52", // orange — primary accent
        slate: "#BDD9F2", // light steel blue — contrast surface
        taupe: "#F2F2F2", // near white — muted text
      },
    },
  },
  plugins: [],
};

export default config;
