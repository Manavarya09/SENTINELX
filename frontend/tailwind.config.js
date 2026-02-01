/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark SOC theme colors
        background: '#0B0F19',
        surface: '#1A1F2E',
        primary: '#00D4FF',
        secondary: '#7C3AED',
        accent: '#F59E0B',
        critical: '#EF4444',
        warning: '#F59E0B',
        success: '#10B981',
        info: '#3B82F6',
        muted: '#64748B',
        border: '#334155'
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(0, 212, 255, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(0, 212, 255, 0.8)' }
        }
      }
    },
  },
  plugins: [],
}