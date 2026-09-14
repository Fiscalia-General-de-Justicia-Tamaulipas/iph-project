/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        institucional: {
          base: "#dadada",
          medio: "#878787",
          oscuro: "#575756",
          fondo: "#f3f3f3",
          texto: "#1f1f1e",
        },
      },
      boxShadow: {
        institucional: "0 18px 45px rgba(87, 87, 86, 0.14)",
      },
    },
  },
  plugins: [],
};
