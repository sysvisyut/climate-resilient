import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { Box } from '@mui/material';
import Login from '../components/Login';
import { isAuthenticated, isAdmin } from '../utils/auth';

export default function LoginPage() {
  const router = useRouter();

  useEffect(() => {
    // If already authenticated, redirect to appropriate dashboard
    if (isAuthenticated()) {
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
        bgcolor: '#f5f5f5',
      }}
    >
      <Login />
    </Box>
  );
}
