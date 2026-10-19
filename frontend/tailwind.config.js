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
        // Palette from the Roots & Roads site: terracotta, river teal, sunshine
        roots: {
          50: '#fbf1ee',
          100: '#f6ded8',
          200: '#efc2b8',
          300: '#e78f81',
          400: '#d9766a',
          500: '#c55f51',
          600: '#a94c40',
          700: '#8a3d34',
          800: '#6b302a',
          900: '#4e2420',
        },
        road: {
          50: '#eef6f8',
          100: '#d7eaee',
          200: '#b5d9e1',
          300: '#8ac6d1',
          400: '#6faebb',
          500: '#5b95a3',
          600: '#4a7b88',
          700: '#3d6470',
          800: '#314f59',
          900: '#263e46',
        },
        sun: {
          100: '#fbf0c6',
          200: '#f8e38f',
          300: '#f4d35e',
          400: '#e8bf3c',
          500: '#d4a72c',
          600: '#b08a22',
        },
        ink: '#2a2826',
        cream: '#fdfcf6',
        // Theme-aware colors using CSS variables
        'bg-primary': 'rgb(var(--color-bg-primary) / <alpha-value>)',
        'bg-secondary': 'rgb(var(--color-bg-secondary) / <alpha-value>)',
        'bg-tertiary': 'rgb(var(--color-bg-tertiary) / <alpha-value>)',
        'text-primary': 'rgb(var(--color-text-primary) / <alpha-value>)',
        'text-secondary': 'rgb(var(--color-text-secondary) / <alpha-value>)',
        'text-tertiary': 'rgb(var(--color-text-tertiary) / <alpha-value>)',
        'border-primary': 'rgb(var(--color-border-primary) / <alpha-value>)',
        'border-secondary': 'rgb(var(--color-border-secondary) / <alpha-value>)',
      },
      fontFamily: {
        sans: ['Nunito', 'ui-sans-serif', 'system-ui', '-apple-system', 'PingFang SC', 'Microsoft YaHei', 'sans-serif'],
        display: ['Quicksand', 'Nunito', 'ui-sans-serif', 'system-ui', 'PingFang SC', 'sans-serif'],
        brand: ['ui-serif', 'Georgia', 'Cambria', '"Times New Roman"', 'Songti SC', 'serif'],
      },
      boxShadow: {
        // Soft coloured glow used on primary buttons, as on Roots & Roads
        'glow-roots': '0 4px 14px 0 rgba(197, 95, 81, 0.39)',
        'glow-road': '0 4px 14px 0 rgba(91, 149, 163, 0.35)',
        paper: '0 1px 2px rgba(42, 40, 38, 0.04), 0 8px 24px rgba(42, 40, 38, 0.08)',
      },
      backgroundImage: {
        'rainbow-road': 'linear-gradient(to right, #e78f81, #f4d35e, #8ac6d1)',
        'gradient-main': 'linear-gradient(135deg, rgb(var(--color-gradient-start)), rgb(var(--color-gradient-mid)), rgb(var(--color-gradient-end)))',
        'gradient-message-user': 'linear-gradient(135deg, rgb(var(--color-message-user-start)), rgb(var(--color-message-user-mid)), rgb(var(--color-message-user-end)))',
      },
      backgroundColor: {
        'glass': 'var(--glass-bg)',
        'sidebar': 'var(--color-sidebar-bg)',
        'message-assistant': 'var(--color-message-assistant-bg)',
      },
      borderColor: {
        'glass': 'var(--glass-border)',
      },
      animation: {
        'fadeIn': 'fadeIn 0.3s ease-in-out',
        'slideUp': 'slideUp 0.3s ease-out',
        'slideInLeft': 'slideInLeft 0.3s ease-out',
        'slideInRight': 'slideInRight 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
