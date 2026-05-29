import { useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createAppTheme } from './theme/theme';
import { useThemeStore } from './stores/themeStore';
import AppShell from './components/layout/AppShell';
import DashboardPage from './components/Dashboard/DashboardPage';
import UploadPage from './components/Upload/UploadPage';
import PipelineExecutionPage from './components/Pipeline/PipelineExecutionPage';
import ReviewPackPage from './components/Assessment/ReviewPackPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

function App() {
  const { mode } = useThemeStore();
  const theme = useMemo(() => createAppTheme(mode), [mode]);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <AppShell>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/review/:pipelineId?" element={<PipelineExecutionPage />} />
              <Route path="/review-pack/:pipelineId?" element={<ReviewPackPage />} />
              {/* Legacy routes redirect */}
              <Route path="/pipeline/:pipelineId?" element={<PipelineExecutionPage />} />
              <Route path="/assessment/:pipelineId?" element={<ReviewPackPage />} />
            </Routes>
          </AppShell>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
