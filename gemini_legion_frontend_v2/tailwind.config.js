/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        legion: {
          primary: '#4A00E0', // Example primary color (purple)
          secondary: '#8E2DE2', // Example secondary color (lighter purple)
          accent: '#FFC107',    // Example accent color (amber)
          background: '#121212', // Dark background
          surface: '#1E1E1E',    // Slightly lighter surface for cards
          text_primary: '#E0E0E0',
          text_secondary: '#B0B0B0',
        }
      }
    },
  },
  plugins: [],
}
