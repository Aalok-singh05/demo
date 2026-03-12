/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#000000',
        card: 'rgba(20, 20, 20, 0.65)',
        primary: '#3b82f6',
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        text: {
          primary: '#FFFFFF',
          secondary: '#AFAFAF'
        },
        agents: {
          chronos: '#60a5fa',
          hermes: '#34d399',
          apollo: '#a78bfa',
          athena: '#fb923c'
        }
      }
    },
  },
  plugins: [],
}
