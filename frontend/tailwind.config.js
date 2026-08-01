/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: {
          light: "#f8fafc",
          dark: "#0b0f19",
        },
        panel: {
          light: "#ffffff",
          dark: "#151d30",
        },
        accent: {
          primary: "#6366f1",  // Indigo
          secondary: "#10b981",  // Emerald
          cyan: "#06b6d4",
          violet: "#8b5cf6",
          dark: "#4f46e5"
        },
        border: {
          light: "#e2e8f0",
          dark: "#1e293b",
        }
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
