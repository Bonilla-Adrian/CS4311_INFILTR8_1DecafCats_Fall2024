import flowbitePlugin from 'flowbite/plugin';
import type { Config } from 'tailwindcss';

// Define and type the configuration
const config: Config = {
  content: [
    './src/**/*.{html,js,svelte,ts}',
    './node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}'
  ],
  darkMode: 'class',  // Class-based dark mode for manual toggling

  theme: {
    extend: {
      colors: {
        // Primary color palette from flowbite-svelte
        primary: {
          50: '#FFF5F2',
          100: '#FFF1EE',
          200: '#FFE4DE',
          300: '#FFD5CC',
          400: '#FFBCAD',
          500: '#FE795D',
          600: '#EF562F',
          700: '#EB4F27',
          800: '#CC4522',
          900: '#A5371B',
        },
        // Custom color schemes for colorblind users
        colorblind: {
          default: {
            bg: '#ffffff',
            text: '#000000',
            primary: '#3b82f6',  // Blue
            danger: '#ef4444',   // Red
          },
          protanopia: {
            bg: '#ffffff',
            text: '#000000',
            primary: '#4a90e2',  // Blue
            danger: '#ffae42',   // Orange
          },
          deuteranopia: {
            bg: '#ffffff',
            text: '#000000',
            primary: '#2874a6',  // Deep Blue
            danger: '#f39c12',   // Yellow
          },
          tritanopia: {
            bg: '#ffffff',
            text: '#000000',
            primary: '#d63031',  // Red
            danger: '#6c5ce7',   // Purple
          }
        }
      }
    }
  },
  plugins: [flowbitePlugin],
};

// Export the configuration
export default config;
