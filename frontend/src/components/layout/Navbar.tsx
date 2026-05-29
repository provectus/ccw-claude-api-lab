import type React from 'react';
import { AppBar, Toolbar, IconButton, Typography, Box, Tooltip } from '@mui/material';
import {
  Menu as MenuIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
} from '@mui/icons-material';
import { useThemeStore } from '../../stores/themeStore';

interface NavbarProps {
  drawerWidth: number;
  onDrawerToggle: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ drawerWidth, onDrawerToggle }) => {
  const { mode, toggleTheme } = useThemeStore();

  return (
    <AppBar
      position="fixed"
      sx={{
        width: { md: `calc(100% - ${drawerWidth}px)` },
        ml: { md: `${drawerWidth}px` },
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        backgroundColor: 'background.paper',
        color: 'text.primary',
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={onDrawerToggle}
          sx={{ mr: 2, display: { md: 'none' } }}
        >
          <MenuIcon />
        </IconButton>

        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
          NAV Review Analyst
        </Typography>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title={`Switch to ${mode === 'light' ? 'dark' : 'light'} mode`}>
            <IconButton onClick={toggleTheme} color="inherit">
              {mode === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
