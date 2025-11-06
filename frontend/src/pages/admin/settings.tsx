import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { 
  Box, 
  Paper, 
  Typography, 
  Grid, 
  Button, 
  Card,
  CardContent,
  CardActions,
  Alert,
  Divider,
  CircularProgress,
  Switch,
  FormControlLabel,
  TextField
} from '@mui/material';
import Layout from '../../components/Layout';
import { isAuthenticated, isAdmin } from '../../utils/auth';
import { trainModels, getClimateHealthCorrelation } from '../../utils/api';

export default function AdminSettingsPage() {
  const router = useRouter();
  const [isTraining, setIsTraining] = useState(false);
  const [trainSuccess, setTrainSuccess] = useState(false);
  const [trainError, setTrainError] = useState('');
  const [correlationData, setCorrelationData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Check if user is authenticated and is admin
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    
    if (!isAdmin()) {
      router.push('/hospital/dashboard');
      return;
    }

    // Fetch correlation data
    const fetchCorrelationData = async () => {
      try {
        setIsLoading(true);
        const data = await getClimateHealthCorrelation();
        setCorrelationData(data);
        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching correlation data:', err);
        setError('Failed to load correlation data');
        setIsLoading(false);
      }
    };

    fetchCorrelationData();
  }, [router]);

  const handleTrainModels = async () => {
    try {
      setIsTraining(true);
      setTrainSuccess(false);
      setTrainError('');
      
      await trainModels();
      
      setTrainSuccess(true);
      setIsTraining(false);
    } catch (err: any) {
      console.error('Error training models:', err);
      setTrainError(err.response?.data?.detail || 'Failed to train models');
      setIsTraining(false);
    }
  };

  return (
    <Layout title="Admin Settings">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          System Administration
        </Typography>
        <Typography variant="body1">
          Manage system settings and model training.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom>
              ML Model Management
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            <Card variant="outlined" sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Model Training
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Train or retrain the ML models using the current data in the database. This will update all prediction models.
                </Typography>
                
                {trainSuccess && (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    Models trained successfully!
                  </Alert>
                )}
                
                {trainError && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {trainError}
                  </Alert>
                )}
              </CardContent>
              <CardActions>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={handleTrainModels}
                  disabled={isTraining}
                  startIcon={isTraining ? <CircularProgress size={20} /> : null}
                >
                  {isTraining ? 'Training...' : 'Train Models'}
                </Button>
              </CardActions>
            </Card>
            
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Alert Thresholds
                </Typography>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="High risk alerts"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Critical risk alerts"
                />
                <TextField
                  label="Risk Probability Threshold"
                  type="number"
                  defaultValue={0.7}
                  InputProps={{ inputProps: { min: 0, max: 1, step: 0.05 } }}
                  helperText="Minimum probability to trigger alerts (0-1)"
                  margin="normal"
                  size="small"
                  sx={{ mt: 2 }}
                />
              </CardContent>
            </Card>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom>
              Climate-Health Correlations
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            {isLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : error ? (
              <Alert severity="error">{error}</Alert>
            ) : correlationData ? (
              <>
                <Typography variant="subtitle1" gutterBottom>
                  Climate Factor Influence on Diseases
                </Typography>
                
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  {Object.entries(correlationData.correlations).map(([disease, factors]: [string, any]) => (
                    <Grid item xs={12} sm={6} key={disease}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            {disease.charAt(0).toUpperCase() + disease.slice(1)}
                          </Typography>
                          {Object.entries(factors).map(([factor, correlation]: [string, any]) => (
                            <Box 
                              key={factor}
                              sx={{ 
                                display: 'flex', 
                                justifyContent: 'space-between',
                                mb: 1 
                              }}
                            >
                              <Typography variant="body2">
                                {factor.charAt(0).toUpperCase() + factor.slice(1)}:
                              </Typography>
                              <Typography 
                                variant="body2" 
                                fontWeight="bold"
                                color={
                                  parseFloat(correlation) > 0.7 ? 'error.main' :
                                  parseFloat(correlation) > 0.4 ? 'warning.main' :
                                  parseFloat(correlation) > 0.2 ? 'info.main' : 'text.secondary'
                                }
                              >
                                {parseFloat(correlation).toFixed(2)}
                              </Typography>
                            </Box>
                          ))}
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
                
                <Typography variant="subtitle1" gutterBottom>
                  Interpretation:
                </Typography>
                
                {Object.entries(correlationData.interpretation).map(([disease, interpretation]: [string, any]) => (
                  <Typography key={disease} variant="body2" paragraph>
                    <strong>{disease.charAt(0).toUpperCase() + disease.slice(1)}:</strong> {interpretation}
                  </Typography>
                ))}
              </>
            ) : null}
          </Paper>
        </Grid>
      </Grid>
    </Layout>
  );
}
