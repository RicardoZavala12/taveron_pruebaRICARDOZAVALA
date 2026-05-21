/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Paleta inspirada en Taveron: azul vivo + cian y un fondo oscuro casi negro.
        brand: {
          50: '#e6f0ff',
          100: '#cce1ff',
          200: '#99c2ff',
          300: '#66a3ff',
          400: '#3385ff',
          500: '#0066ff',
          600: '#0052cc',
          700: '#003d99',
          800: '#002966',
          900: '#001433',
        },
        aqua: {
          400: '#22d3ee',
          500: '#06b6d4',
        },
        ink: {
          900: '#0a1929',
          800: '#0f2237',
          700: '#15324f',
        },
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        pill: '9999px',
        card: '24px',
      },
      boxShadow: {
        soft: '0 10px 30px -12px rgba(15, 34, 55, 0.25)',
      },
    },
  },
  plugins: [],
}
