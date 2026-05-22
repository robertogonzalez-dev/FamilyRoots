/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#f0f4ff",
          100: "#dde7ff",
          200: "#c0cffe",
          300: "#93affe",
          400: "#607ffc",
          500: "#3b57f9",
          600: "#2435ee",
          700: "#1c28d9",
          800: "#1d25af",
          900: "#1d2689",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
