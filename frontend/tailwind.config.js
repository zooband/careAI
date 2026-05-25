/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd3f0',
          300: '#c4b0e3',
          400: '#a78bc9',
          500: '#8b6fae',
          600: '#6B4E8A',
          700: '#553d6e',
          800: '#453258',
          900: '#3a2a4a',
        },
        warm: {
          50: '#FDF8F0',
          100: '#F9F0E0',
          200: '#F3E0C0',
          300: '#E8C890',
          400: '#DBA860',
          500: '#D09040',
          600: '#C07830',
          700: '#A06028',
          800: '#804820',
          900: '#603018',
        },
        accent: {
          DEFAULT: '#E8923E',
          light: '#FFB366',
          dark: '#D07820',
        },
      },
      fontFamily: {
        sans: [
          '"Noto Sans SC"', '"PingFang SC"', '"Microsoft YaHei"',
          'ui-sans-serif', 'system-ui', 'sans-serif',
        ],
      },
      borderRadius: {
        '2xl': '16px',
        '3xl': '24px',
      },
    },
  },
  plugins: [],
}
