/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'palette-bg': '#100a18',
        'palette-dark': '#3b2b54',
        'palette-mid': '#5459AC',
        'palette-light': '#6B90B2',
        'palette-mint': '#B3D8C8',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
