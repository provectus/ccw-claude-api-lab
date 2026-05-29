import { createTheme } from '@mui/material/styles';
import type { ThemeOptions } from '@mui/material/styles';

const lightColors = {
  primary: '#0A1628',
  secondary: '#00897B',
  success: '#2E7D32',
  warning: '#F57F17',
  error: '#C62828',
  background: '#FAFAFA',
  surface: '#FFFFFF',
  text: '#1A1A2E',
};

const darkColors = {
  primary: '#5DADE2',
  secondary: '#4DB6AC',
  success: '#66BB6A',
  warning: '#FFCA28',
  error: '#EF5350',
  background: '#121212',
  surface: '#1E1E1E',
  text: '#E0E0E0',
};

const getThemeOptions = (mode: 'light' | 'dark'): ThemeOptions => {
  const colors = mode === 'light' ? lightColors : darkColors;

  return {
    palette: {
      mode,
      primary: { main: colors.primary },
      secondary: { main: colors.secondary },
      success: { main: colors.success },
      warning: { main: colors.warning },
      error: { main: colors.error },
      background: {
        default: colors.background,
        paper: colors.surface,
      },
      text: {
        primary: colors.text,
        secondary: mode === 'light'
          ? 'rgba(26, 26, 46, 0.7)'
          : 'rgba(224, 224, 224, 0.7)',
      },
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h1: { fontSize: '2.5rem', fontWeight: 700, lineHeight: 1.2 },
      h2: { fontSize: '2rem', fontWeight: 600, lineHeight: 1.3 },
      h3: { fontSize: '1.75rem', fontWeight: 600, lineHeight: 1.3 },
      h4: { fontSize: '1.5rem', fontWeight: 600, lineHeight: 1.4 },
      h5: { fontSize: '1.25rem', fontWeight: 600, lineHeight: 1.4 },
      h6: { fontSize: '1rem', fontWeight: 600, lineHeight: 1.5 },
      body1: { fontSize: '1rem', lineHeight: 1.5 },
      body2: { fontSize: '0.875rem', lineHeight: 1.5 },
      button: { textTransform: 'none', fontWeight: 500 },
    },
    shape: { borderRadius: 8 },
    components: {
      MuiButton: {
        styleOverrides: {
          root: { borderRadius: 8, padding: '8px 16px', fontSize: '0.875rem' },
          contained: { boxShadow: 'none', '&:hover': { boxShadow: 'none' } },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            boxShadow: mode === 'light'
              ? '0 2px 8px rgba(0, 0, 0, 0.08)'
              : '0 2px 8px rgba(0, 0, 0, 0.3)',
          },
        },
      },
      MuiPaper: {
        styleOverrides: { root: { backgroundImage: 'none' } },
      },
      MuiTextField: {
        styleOverrides: {
          root: { '& .MuiOutlinedInput-root': { borderRadius: 8 } },
        },
      },
      MuiChip: {
        styleOverrides: { root: { borderRadius: 6 } },
      },
    },
  };
};

export const createAppTheme = (mode: 'light' | 'dark') => {
  return createTheme(getThemeOptions(mode));
};
