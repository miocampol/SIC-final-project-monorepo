/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        prisma: {
          bg: '#131314', // Neutral dark (Gemini style)
          surface: '#1E1F20', // Neutral surface
          hover: '#2D2E30', // Neutral hover
          text: '#E3E3E3', // Off-white text
          input: '#1E1F20', // Input background (same as surface)
          accent: '#a78bfa', // Purple accent (violet-400)
        }
      },
      keyframes: {
        gradient: {
          '0%, 100%': { 'background-position': '0% 50%' },
          '50%': { 'background-position': '100% 50%' },
        }
      },
      animation: {
        gradient: 'gradient 3s ease infinite',
      }
    },
  },
  plugins: [],
}
