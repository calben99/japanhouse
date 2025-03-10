/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'jp-red': '#D73434',
        'jp-navy': '#1F2937',
        'jp-gray': '#6B7280',
        'jp-light': '#F3F4F6',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
