import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Material 3 Design System Colors
        primary: {
          DEFAULT: '#6750A4',
          50: '#F5F3FF',
          100: '#EDE9FE',
          200: '#DDD6FE',
          300: '#C4B5FD',
          400: '#A78BFA',
          500: '#6750A4',
          600: '#5A3E96',
          700: '#4A2E7D',
          800: '#3A1F63',
          900: '#2A0F49',
        },
        secondary: {
          DEFAULT: '#625B71',
          50: '#F8F7FA',
          100: '#EFEDF4',
          200: '#E0DCE9',
          300: '#CCC2DC',
          400: '#B8AFCC',
          500: '#625B71',
          600: '#544C63',
          700: '#463D52',
          800: '#382E41',
          900: '#2A1F30',
        },
        tertiary: {
          DEFAULT: '#7D5260',
          50: '#FEF7F9',
          100: '#FCEEF3',
          200: '#F9DEE7',
          300: '#F5CED9',
          400: '#EFBDC9',
          500: '#7D5260',
          600: '#6D4653',
          700: '#5D3A46',
          800: '#4D2E39',
          900: '#3D222C',
        },
        surface: {
          DEFAULT: '#1C1B1F',
          dim: '#141218',
          bright: '#3B383E',
          container: {
            DEFAULT: '#211F26',
            low: '#1C1B1F',
            high: '#2B2930',
            highest: '#36343B',
          },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'glass': 'linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0))',
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

export default config
