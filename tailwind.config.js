/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#050505",
        surface: "#0d0d12",
        surface2: "#16161d",
        accent: "#00e5ff",
        accent_dim: "#00a3b8",
        danger: "#ff3c6e",
        success: "#7fff6e",
        warning: "#f5c842",
        muted: "#8fa0b8",
        border: "rgba(0,229,255,0.08)",
        gold: "#d4af37",
      },
      fontFamily: {
        space: ["var(--font-space)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
        inter: ["var(--font-inter)", "sans-serif"],
        newsreader: ["var(--font-newsreader)", "serif"],
        manrope: ["var(--font-manrope)", "sans-serif"],
      },
      backgroundImage: {
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
};
