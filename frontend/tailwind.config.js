/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'primary': '#856199', // Muted Purple from screenshot
                'crm-header': '#FBF6E7', // Pale beige header
                'crm-purple': '#856199', // Divider purple
                'crm-link': '#057A9F', // Teal/Blue links
                'secondary': '#312E2B',
                'surface': '#FFFFFF', // White background for main content
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
