import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { Box, Paper, Typography, Grid, Card, CardContent, Alert, AlertTitle, CircularProgress } from '@mui/material';
import Layout from '../components/Layout';
import { isAuthenticated, getUserLocationId, isAdmin } from '../utils/auth';
import { getAlerts } from '../utils/api';

export default function AlertsPage() {
  const router = useRouter();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const userLocationId = getUserLocationId();
  const adminUser = isAdmin();

  useEffect(() => {
    // Check if user is authenticated
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    // Fetch alerts
    const fetchAlerts = async () => {
      try {
        setIsLoading(true);
        const data = await getAlerts(0.7); // Risk threshold of 0.7
        
        // Filter alerts for hospital users to only show their location
        if (!adminUser && userLocationId) {
          setAlerts(data.alerts.filter((alert: any) => alert.location_id === userLocationId));
        } else {
          setAlerts(data.alerts);
        }
        
        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching alerts:', err);
        setError('Failed to load alerts');
        setIsLoading(false);
      }
    };

    fetchAlerts();
  }, [router, adminUser, userLocationId]);

  return (
    <Layout title="Health Risk Alerts">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Health Risk Alerts
        </Typography>
        <Typography variant="body1">
          Critical health risk alerts based on current climate conditions.
        </Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 3 }}>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : alerts.length === 0 ? (
          <Alert severity="success">
            <AlertTitle>No Critical Alerts</AlertTitle>
            There are currently no high-risk health alerts that require immediate attention.
          </Alert>
        ) : (
          <Grid container spacing={3}>
            {alerts.map((alert, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Alert 
                  severity={
                    alert.risk_level === 'critical' ? 'error' : 
                    alert.risk_level === 'high' ? 'warning' : 'info'
                  }
                  sx={{ mb: 2 }}
                >
                  <AlertTitle>
                    {alert.disease.toUpperCase()} - {alert.location_name}
                  </AlertTitle>
                  <Typography variant="body1">
                    {alert.message}
                  </Typography>
                  <Typography variant="body2">
                    Risk Level: {alert.risk_level.toUpperCase()}
                  </Typography>
                  <Typography variant="body2">
                    Probability: {Math.round(alert.probability * 100)}%
                  </Typography>
                </Alert>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>
    </Layout>
  );
}
