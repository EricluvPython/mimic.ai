import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{ts,tsx,js,jsx}',
    './components/**/*.{ts,tsx,js,jsx}',
    './pages/**/*.{ts,tsx,js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        mimic: {
          dark: '#0f172a',
          teal: '#0b7b6b',
          accent: '#1be38a',
          accent2: '#6ac6ff',
          glass: 'rgba(255,255,255,0.06)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      borderRadius: {
        'mimic': '14px',
      },
    },
  },
  plugins: [],
}
export default config
