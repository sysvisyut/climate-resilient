import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { Box } from '@mui/material';
import Layout from '../../components/Layout';
import Dashboard from '../../components/Dashboard';
import { isAuthenticated, isAdmin, getUserLocationId } from '../../utils/auth';

export default function HospitalDashboardPage() {
  const router = useRouter();
  const userLocationId = getUserLocationId();

  useEffect(() => {
    // Check if user is authenticated
    if (!isAuthenticated()) {
      router.push('/login');
    } else if (isAdmin()) {
      router.push('/admin/dashboard'); // Redirect to admin dashboard if admin
    }
  }, [router]);

  return (
    <Layout title="Hospital Dashboard">
      <Dashboard userRole="hospital" userLocationId={userLocationId} />
    </Layout>
  );
}
