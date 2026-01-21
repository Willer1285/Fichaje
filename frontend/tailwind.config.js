/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#4318FF",
        secondary: "#6AD2FF",
        sidebar: "#111C44",
        background: "#F4F7FE",
        success: "#05CD99",
        warning: "#FFB547",
        error: "#EE5D50"
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
