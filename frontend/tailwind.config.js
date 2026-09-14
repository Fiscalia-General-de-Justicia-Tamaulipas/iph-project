/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        institucional: {
          oscuro: "#2c2c26",
          verde: "#4b4b3f",
          dorado: "#a89968",
          claro: "#f2f2ee",
        },
      },
    },
  },
  plugins: [],
};
