import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { Box } from '@mui/material';
import Layout from '../../components/Layout';
import Dashboard from '../../components/Dashboard';
import { isAuthenticated, isAdmin } from '../../utils/auth';

export default function AdminDashboardPage() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated and is an admin
    if (!isAuthenticated()) {
      router.push('/login');
    } else if (!isAdmin()) {
      router.push('/hospital/dashboard'); // Redirect to hospital dashboard if not admin
    }
  }, [router]);

  return (
    <Layout title="Admin Dashboard">
      <Dashboard userRole="admin" />
    </Layout>
  );
}
