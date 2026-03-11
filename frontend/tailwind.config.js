/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0f1e',
        card: '#111827',
        primary: '#3b82f6',
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        text: {
          primary: '#f9fafb',
          secondary: '#9ca3af'
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
