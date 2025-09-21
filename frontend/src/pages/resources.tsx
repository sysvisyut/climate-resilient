import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { 
  Box, 
  Paper, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  Alert, 
  AlertTitle,
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  CircularProgress,
  LinearProgress,
  Divider
} from '@mui/material';
import Layout from '../components/Layout';
import { isAuthenticated, getUserLocationId } from '../utils/auth';
import { getLocations, predictResources } from '../utils/api';

export default function ResourcesPage() {
  const router = useRouter();
  const [locations, setLocations] = useState<any[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<number | null>(null);
  const [resourceData, setResourceData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [error, setError] = useState('');
  const userLocationId = getUserLocationId();

  useEffect(() => {
    // Check if user is authenticated
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    // Fetch locations
    const fetchLocations = async () => {
      try {
        setIsFetching(true);
        const locationsData = await getLocations();
        setLocations(locationsData);
        
        // For hospital users, pre-select their location
        if (userLocationId) {
          setSelectedLocation(userLocationId);
          fetchResourceData(userLocationId);
        }
        
        setIsFetching(false);
      } catch (err) {
        console.error('Error fetching locations:', err);
        setError('Failed to load locations');
        setIsFetching(false);
      }
    };

    fetchLocations();
  }, [router, userLocationId]);

  const fetchResourceData = async (locationId: number) => {
    try {
      setIsLoading(true);
      setError('');
      const data = await predictResources(locationId);
      setResourceData(data);
      setIsLoading(false);
    } catch (err: any) {
      console.error('Error fetching resource data:', err);
      setError(err.response?.data?.detail || 'Failed to load resource data');
      setIsLoading(false);
    }
  };

  const handleLocationChange = (event: any) => {
    const locationId = event.target.value;
    setSelectedLocation(locationId);
    fetchResourceData(locationId);
  };

  // Function to calculate the percentage of resources available vs needed
  const calculatePercentage = (available: number, predicted: number) => {
    if (predicted === 0) return 100; // No need
    const percentage = (available / predicted) * 100;
    return Math.min(100, Math.max(0, percentage)); // Clamp between 0-100
  };

  // Function to determine the resource status color
  const getResourceStatusColor = (percentage: number) => {
    if (percentage >= 100) return 'success.main';
    if (percentage >= 70) return 'warning.main';
    return 'error.main';
  };

  return (
    <Layout title="Hospital Resources">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Hospital Resource Management
        </Typography>
        <Typography variant="body1">
          Current resources, predicted needs, and recommendations for optimal healthcare delivery.
        </Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 3 }}>
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel id="location-select-label">Select Location</InputLabel>
          <Select
            labelId="location-select-label"
            value={selectedLocation || ''}
            onChange={handleLocationChange}
            label="Select Location"
            disabled={isFetching}
          >
            {locations.map((location) => (
              <MenuItem key={location.id} value={location.id}>
                {location.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {isFetching ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : !selectedLocation ? (
          <Alert severity="info">Please select a location to view resource information</Alert>
        ) : isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : resourceData ? (
          <>
            <Typography variant="h6" gutterBottom>
              Resource Analysis for {resourceData.location.name}
            </Typography>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Date: {resourceData.date}
            </Typography>
            
            <Grid container spacing={3} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Hospital Beds
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body1" sx={{ mr: 1 }}>
                        Available: {resourceData.current_resources.beds}
                      </Typography>
                      <Typography variant="body1" sx={{ ml: 'auto', fontWeight: 'bold' }}>
                        Needed: {resourceData.predicted_resources.beds}
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={calculatePercentage(resourceData.current_resources.beds, resourceData.predicted_resources.beds)}
                      color={getResourceStatusColor(calculatePercentage(resourceData.current_resources.beds, resourceData.predicted_resources.beds)) === 'success.main' ? 'success' : 
                             getResourceStatusColor(calculatePercentage(resourceData.current_resources.beds, resourceData.predicted_resources.beds)) === 'warning.main' ? 'warning' : 'error'}
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                    {resourceData.resource_gaps.beds > 0 && (
                      <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                        Gap: {resourceData.resource_gaps.beds} beds needed
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Medical Staff
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body1" sx={{ mr: 1 }}>
                        Doctors: {resourceData.current_resources.doctors}
                      </Typography>
                      <Typography variant="body1" sx={{ ml: 'auto', fontWeight: 'bold' }}>
                        Needed: {resourceData.predicted_resources.doctors}
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={calculatePercentage(resourceData.current_resources.doctors, resourceData.predicted_resources.doctors)}
                      color={getResourceStatusColor(calculatePercentage(resourceData.current_resources.doctors, resourceData.predicted_resources.doctors)) === 'success.main' ? 'success' : 
                             getResourceStatusColor(calculatePercentage(resourceData.current_resources.doctors, resourceData.predicted_resources.doctors)) === 'warning.main' ? 'warning' : 'error'}
                      sx={{ height: 10, borderRadius: 5, mb: 2 }}
                    />
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body1" sx={{ mr: 1 }}>
                        Nurses: {resourceData.current_resources.nurses}
                      </Typography>
                      <Typography variant="body1" sx={{ ml: 'auto', fontWeight: 'bold' }}>
                        Needed: {resourceData.predicted_resources.nurses}
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={calculatePercentage(resourceData.current_resources.nurses, resourceData.predicted_resources.nurses)}
                      color={getResourceStatusColor(calculatePercentage(resourceData.current_resources.nurses, resourceData.predicted_resources.nurses)) === 'success.main' ? 'success' : 
                             getResourceStatusColor(calculatePercentage(resourceData.current_resources.nurses, resourceData.predicted_resources.nurses)) === 'warning.main' ? 'warning' : 'error'}
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Medical Supplies
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="subtitle1">IV Fluids</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Typography variant="body2" sx={{ mr: 1 }}>
                            Available: {resourceData.current_resources.iv_fluids}
                          </Typography>
                          <Typography variant="body2" sx={{ ml: 'auto' }}>
                            Needed: {resourceData.predicted_resources.iv_fluids}
                          </Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={calculatePercentage(resourceData.current_resources.iv_fluids, resourceData.predicted_resources.iv_fluids)}
                          color={getResourceStatusColor(calculatePercentage(resourceData.current_resources.iv_fluids, resourceData.predicted_resources.iv_fluids)) === 'success.main' ? 'success' : 
                                 getResourceStatusColor(calculatePercentage(resourceData.current_resources.iv_fluids, resourceData.predicted_resources.iv_fluids)) === 'warning.main' ? 'warning' : 'error'}
                          sx={{ height: 8, borderRadius: 5 }}
                        />
                      </Grid>
                      
                      <Grid item xs={12} sm={4}>
                        <Typography variant="subtitle1">Antibiotics</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Typography variant="body2" sx={{ mr: 1 }}>
                            Available: {resourceData.current_resources.antibiotics}
                          </Typography>
                          <Typography variant="body2" sx={{ ml: 'auto' }}>
                            Needed: {resourceData.predicted_resources.antibiotics}
                          </Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={calculatePercentage(resourceData.current_resources.antibiotics, resourceData.predicted_resources.antibiotics)}
                          color={getResourceStatusColor(calculatePercentage(resourceData.current_resources.antibiotics, resourceData.predicted_resources.antibiotics)) === 'success.main' ? 'success' : 
                                 getResourceStatusColor(calculatePercentage(resourceData.current_resources.antibiotics, resourceData.predicted_resources.antibiotics)) === 'warning.main' ? 'warning' : 'error'}
                          sx={{ height: 8, borderRadius: 5 }}
                        />
                      </Grid>
                      
                      <Grid item xs={12} sm={4}>
                        <Typography variant="subtitle1">Antipyretics</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Typography variant="body2" sx={{ mr: 1 }}>
                            Available: {resourceData.current_resources.antipyretics}
                          </Typography>
                          <Typography variant="body2" sx={{ ml: 'auto' }}>
                            Needed: {resourceData.predicted_resources.antipyretics}
                          </Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={calculatePercentage(resourceData.current_resources.antipyretics, resourceData.predicted_resources.antipyretics)}
                          color={getResourceStatusColor(calculatePercentage(resourceData.current_resources.antipyretics, resourceData.predicted_resources.antipyretics)) === 'success.main' ? 'success' : 
                                 getResourceStatusColor(calculatePercentage(resourceData.current_resources.antipyretics, resourceData.predicted_resources.antipyretics)) === 'warning.main' ? 'warning' : 'error'}
                          sx={{ height: 8, borderRadius: 5 }}
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Resource Recommendations
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    
                    {resourceData.recommendations.length === 0 ? (
                      <Alert severity="success">
                        <AlertTitle>Resources Sufficient</AlertTitle>
                        Current resources are adequate for predicted health needs
                      </Alert>
                    ) : (
                      <>
                        <Typography variant="subtitle1" gutterBottom>
                          Immediate Actions Required:
                        </Typography>
                        <Grid container spacing={2}>
                          {resourceData.recommendations.map((rec: any, idx: number) => (
                            <Grid item xs={12} sm={6} key={idx}>
                              <Alert severity="warning" sx={{ mb: 1 }}>
                                <AlertTitle>{rec.resource.toUpperCase()}</AlertTitle>
                                {rec.message}
                              </Alert>
                            </Grid>
                          ))}
                        </Grid>
                      </>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </>
        ) : null}
      </Paper>
    </Layout>
  );
}
