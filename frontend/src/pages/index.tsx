import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { Box, CircularProgress, Typography } from '@mui/material';
import { isAuthenticated, isAdmin } from '../utils/auth';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check authentication and redirect accordingly
    if (!isAuthenticated()) {
      router.push('/login');
    } else {
      // Redirect based on role
      if (isAdmin()) {
        router.push('/admin/dashboard');
      } else {
        router.push('/hospital/dashboard');
      }
    }
  }, [router]);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
      }}
    >
      <Typography variant="h4" gutterBottom>
        Climate-Resilient Healthcare System
      </Typography>
      <CircularProgress />
      <Typography variant="body1" sx={{ mt: 2 }}>
        Redirecting...
      </Typography>
    </Box>
  );
}
