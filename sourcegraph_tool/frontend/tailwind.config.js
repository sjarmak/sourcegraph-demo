/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Sourcegraph color palette
        sourcegraph: {
          50: '#f8faff',
          100: '#f1f5ff',
          200: '#e1ecff',
          300: '#c9ddff',
          400: '#9fc5ff',
          500: '#6ba6ff',
          600: '#2b4eff', // Primary Sourcegraph blue
          700: '#1e3a8a',
          800: '#1e2a5e',
          900: '#0f1419',
        },
        // Neutral grays for text and backgrounds
        neutral: {
          50: '#fafbfc',
          100: '#f4f6f8',
          200: '#e9ecef',
          300: '#d1d9e0',
          400: '#a2a8b4',
          500: '#5e6e8c',
          600: '#343a46',
          700: '#24292e',
          800: '#1b1f23',
          900: '#0d1117',
        },
        // Semantic colors
        success: '#28a745',
        warning: '#ffc107',
        error: '#dc3545',
        info: '#17a2b8',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'Consolas', 'monospace'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
    },
  },
  plugins: [],
}
