/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./themes/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        primary: "#634CF1",
        highlight: "#DCDDFC",
        primarylight: "#6E70AA",
        primarydark: "#27204E"
      },
    },
  },
  plugins: [],
};
