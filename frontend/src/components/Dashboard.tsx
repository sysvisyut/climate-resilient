import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  Tabs,
  Tab,
  CircularProgress,
  Chip,
  Alert,
  AlertTitle,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
} from '@mui/material';
import WaterDropIcon from '@mui/icons-material/WaterDrop';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import WbSunnyIcon from '@mui/icons-material/WbSunny';
import CoronavirusIcon from '@mui/icons-material/Coronavirus';
import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety';
import IndiaMap from './IndiaMap';
import IndiaLeafletMap from './IndiaLeafletMap';
import { getDataSummary, getAlerts, predictRisk, predictResources } from '../utils/api';

interface DashboardProps {
  userRole: 'admin' | 'hospital';
  userLocationId?: number;
}

type LocationOption = {
  location_id: number;
  name: string;
};

const Dashboard = ({ userRole, userLocationId }: DashboardProps) => {
  const [tab, setTab] = useState(0);
  const [mapColorBy, setMapColorBy] = useState<'dengue' | 'malaria' | 'heatstroke' | 'diarrhea' | 'overall'>('overall');
  const [selectedLocation, setSelectedLocation] = useState<{
    id: number;
    name: string;
  } | null>(null);
  
  const [locations, setLocations] = useState<LocationOption[]>([]);
  const [summaryData, setSummaryData] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [riskData, setRiskData] = useState<any>(null);
  const [resourceData, setResourceData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState({
    summary: false,
    alerts: false,
    risk: false,
    resources: false,
  });
  const [error, setError] = useState('');

  useEffect(() => {
    // If user is hospital type, pre-select their location
    if (userRole === 'hospital' && userLocationId) {
      setSelectedLocation({
        id: userLocationId,
        name: 'Your Hospital Location',
      });
      fetchRiskData(userLocationId);
      fetchResourceData(userLocationId);
    }

    fetchSummaryData();
    fetchAlerts();
  }, [userRole, userLocationId]);

  const fetchSummaryData = async () => {
    try {
      setIsLoading((prev) => ({ ...prev, summary: true }));
      const data = await getDataSummary();
      setSummaryData(data);
      
      // Extract and set locations list for dropdown
      if (data && data.locations && Array.isArray(data.locations)) {
        const locationsList: LocationOption[] = data.locations.map((loc: any) => ({
          location_id: Number(loc.location_id),
          name: String(loc.name)
        }));
        
        // Sort locations alphabetically by name
        locationsList.sort((a: LocationOption, b: LocationOption) => a.name.localeCompare(b.name));
        setLocations(locationsList);
        console.log('Loaded locations for dropdown:', locationsList.length);
      }
      
      // Update hospital location name if it exists in the data
      if (userRole === 'hospital' && userLocationId) {
        const locationData = data.locations.find(
          (loc: any) => loc.location_id === userLocationId
        );
        if (locationData) {
          setSelectedLocation({
            id: userLocationId,
            name: locationData.name,
          });
        }
      }
    } catch (err) {
      console.error('Error fetching summary data:', err);
      setError('Failed to load summary data');
    } finally {
      setIsLoading((prev) => ({ ...prev, summary: false }));
    }
  };

  const fetchAlerts = async () => {
    try {
      setIsLoading((prev) => ({ ...prev, alerts: true }));
      const data = await getAlerts();
      
      // Filter alerts for hospital users to only show their location
      if (userRole === 'hospital' && userLocationId) {
        setAlerts(data.alerts.filter((alert: any) => alert.location_id === userLocationId));
      } else {
        setAlerts(data.alerts);
      }
    } catch (err) {
      console.error('Error fetching alerts:', err);
    } finally {
      setIsLoading((prev) => ({ ...prev, alerts: false }));
    }
  };

  const fetchRiskData = async (locationId: number) => {
    try {
      setIsLoading((prev) => ({ ...prev, risk: true }));
      const data = await predictRisk(locationId);
      
      if (!data) {
        console.error('No risk data returned from API');
        setError('Failed to load risk data. Please try again later.');
        return;
      }
      
      console.log('Risk data loaded:', data);
      setRiskData(data);
    } catch (err) {
      console.error('Error fetching risk data:', err);
      setError('Failed to load risk data. Please check your connection and try again.');
    } finally {
      setIsLoading((prev) => ({ ...prev, risk: false }));
    }
  };

  const fetchResourceData = async (locationId: number) => {
    try {
      setIsLoading((prev) => ({ ...prev, resources: true }));
      const data = await predictResources(locationId);
      
      if (!data) {
        console.error('No resource data returned from API');
        setError('Failed to load resource data. Please try again later.');
        return;
      }
      
      console.log('Resource data loaded:', data);
      setResourceData(data);
    } catch (err) {
      console.error('Error fetching resource data:', err);
      setError('Failed to load resource data. Please check your connection and try again.');
    } finally {
      setIsLoading((prev) => ({ ...prev, resources: false }));
    }
  };

  const handleLocationSelect = (locationId: number, locationName: string) => {
    console.log('Location selected:', locationId, locationName);
    
    if (!locationId || isNaN(locationId)) {
      console.error('Invalid location ID:', locationId);
      setError('Invalid location selected. Please try again.');
      return;
    }
    
    // Clear any previous errors
    setError('');
    
    // Update selected location state
    setSelectedLocation({ id: locationId, name: locationName });
    
    // Show loading indicator
    setIsLoading({
      summary: isLoading.summary,
      alerts: isLoading.alerts,
      risk: true,
      resources: true
    });
    
    // Fetch data for the selected location
    Promise.all([
      fetchRiskData(locationId),
      fetchResourceData(locationId)
    ]).then(() => {
      console.log('All data loaded for location:', locationName);
      // Switch to the Risk tab to show the results
      setTab(0);
    }).catch(err => {
      console.error('Error loading location data:', err);
      setError('Failed to load data for the selected location. Please try again.');
    });
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTab(newValue);
  };
  
  const handleLocationDropdownChange = (event: SelectChangeEvent<number>) => {
    const locationId = Number(event.target.value);
    
    if (!locationId || isNaN(locationId)) {
      console.error('Invalid location ID from dropdown:', event.target.value);
      return;
    }
    
    // Find the location name
    const location = locations.find(loc => loc.location_id === locationId);
    if (!location) {
      console.error('Location not found for ID:', locationId);
      return;
    }
    
    // Call the existing handler with the selected location
    handleLocationSelect(locationId, location.name);
  };

  const renderRiskLevel = (level: string) => {
    const colors: Record<string, string> = {
      low: 'success',
      medium: 'warning',
      high: 'error',
      critical: 'error',
    };

    return (
      <Chip
        label={level.toUpperCase()}
        color={colors[level] as any}
        size="small"
        sx={{ fontWeight: 'bold' }}
      />
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        {userRole === 'admin' ? 'Admin Dashboard' : 'Hospital Dashboard'}
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Map Section */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              India Health Risk Map
            </Typography>
            
            <Box sx={{ mb: 2, display: 'flex', gap: 1 }}>
              <Button
                variant={mapColorBy === 'overall' ? 'contained' : 'outlined'}
                color="primary"
                onClick={() => setMapColorBy('overall')}
                startIcon={<HealthAndSafetyIcon />}
                size="small"
              >
                Overall
              </Button>
              <Button
                variant={mapColorBy === 'dengue' ? 'contained' : 'outlined'}
                color="warning"
                onClick={() => setMapColorBy('dengue')}
                startIcon={<CoronavirusIcon />}
                size="small"
              >
                Dengue
              </Button>
              <Button
                variant={mapColorBy === 'malaria' ? 'contained' : 'outlined'}
                color="success"
                onClick={() => setMapColorBy('malaria')}
                startIcon={<CoronavirusIcon />}
                size="small"
              >
                Malaria
              </Button>
              <Button
                variant={mapColorBy === 'heatstroke' ? 'contained' : 'outlined'}
                color="error"
                onClick={() => setMapColorBy('heatstroke')}
                startIcon={<WbSunnyIcon />}
                size="small"
              >
                Heatstroke
              </Button>
              <Button
                variant={mapColorBy === 'diarrhea' ? 'contained' : 'outlined'}
                color="info"
                onClick={() => setMapColorBy('diarrhea')}
                startIcon={<WaterDropIcon />}
                size="small"
              >
                Diarrhea
              </Button>
            </Box>
            
            <Box sx={{ mb: 2, mt: 1 }}>
              <FormControl fullWidth>
                <InputLabel id="location-select-label">Select Location</InputLabel>
                <Select
                  labelId="location-select-label"
                  id="location-select"
                  value={selectedLocation?.id || ''}
                  label="Select Location"
                  onChange={handleLocationDropdownChange}
                >
                  {locations.map((location) => (
                    <MenuItem key={location.location_id} value={location.location_id}>
                      {location.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
            
            <IndiaLeafletMap colorBy={mapColorBy} onLocationClick={handleLocationSelect} />
            <Typography variant="caption" color="text.secondary">
              Click on a state/UT on the map or use the dropdown above to view detailed risk and resource predictions
            </Typography>
          </Paper>
        </Grid>

        {/* Alert Section */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%', overflowY: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              Health Alerts
              {isLoading.alerts && (
                <CircularProgress size={20} sx={{ ml: 2, verticalAlign: 'middle' }} />
              )}
            </Typography>
            
            {alerts.length === 0 ? (
              <Alert severity="success" sx={{ mt: 2 }}>
                No high-risk alerts at this time
              </Alert>
            ) : (
              alerts.map((alert, index) => (
                <Alert severity="warning" sx={{ mt: 2 }} key={index}>
                  <AlertTitle>{alert.disease.toUpperCase()} - {alert.risk_level}</AlertTitle>
                  {alert.message}<br />
                  <Typography variant="caption">
                    Probability: {Math.round(alert.probability * 100)}%
                  </Typography>
                </Alert>
              ))
            )}
          </Paper>
        </Grid>

        {/* Selected Location Details */}
        {selectedLocation && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h5" gutterBottom>
                {selectedLocation.name}
              </Typography>

              <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                <Tabs value={tab} onChange={handleTabChange}>
                  <Tab label="Risk Prediction" />
                  <Tab label="Resource Needs" />
                </Tabs>
              </Box>

              {/* Risk Prediction Tab */}
              {tab === 0 && (
                <Box>
                  {isLoading.risk ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                      <CircularProgress />
                    </Box>
                  ) : riskData ? (
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <Card>
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              Climate Conditions
                            </Typography>
                            <Typography>
                              Temperature: {riskData.climate_data?.temperature ?? 'N/A'}°C
                            </Typography>
                            <Typography>
                              Rainfall: {riskData.climate_data?.rainfall ?? 'N/A'}mm
                            </Typography>
                            <Typography>
                              Humidity: {riskData.climate_data?.humidity ?? 'N/A'}%
                            </Typography>
                            <Typography>
                              Date: {riskData.date ?? 'N/A'}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Card>
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              Disaster Probabilities
                            </Typography>
                            <Typography>
                              Flood: {riskData.climate_data?.flood_probability ? Math.round(riskData.climate_data.flood_probability * 100) : 'N/A'}%
                            </Typography>
                            <Typography>
                              Cyclone: {riskData.climate_data?.cyclone_probability ? Math.round(riskData.climate_data.cyclone_probability * 100) : 'N/A'}%
                            </Typography>
                            <Typography>
                              Heatwave: {riskData.climate_data?.heatwave_probability ? Math.round(riskData.climate_data.heatwave_probability * 100) : 'N/A'}%
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                      <Grid item xs={12}>
                        <Card>
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              Health Risk Predictions
                            </Typography>
                            <Grid container spacing={2}>
                              <Grid item xs={6} md={3}>
                                <Card variant="outlined">
                                  <CardContent>
                                    <Typography variant="subtitle1">Dengue</Typography>
                                    {riskData.risk_prediction?.dengue?.risk_level ? 
                                      renderRiskLevel(riskData.risk_prediction.dengue.risk_level) :
                                      riskData.health_predictions?.dengue?.risk_level ? 
                                        renderRiskLevel(riskData.health_predictions.dengue.risk_level) :
                                        <Chip label="UNKNOWN" color="default" size="small" />
                                    }
                                    <Typography variant="caption" display="block">
                                      Confidence: {Math.round(
                                        (riskData.risk_prediction?.dengue?.probability || 
                                         riskData.health_predictions?.dengue?.probability || 0) * 100
                                      )}%
                                    </Typography>
                                  </CardContent>
                                </Card>
                              </Grid>
                              <Grid item xs={6} md={3}>
                                <Card variant="outlined">
                                  <CardContent>
                                    <Typography variant="subtitle1">Malaria</Typography>
                                    {riskData.risk_prediction?.malaria?.risk_level ? 
                                      renderRiskLevel(riskData.risk_prediction.malaria.risk_level) :
                                      riskData.health_predictions?.malaria?.risk_level ? 
                                        renderRiskLevel(riskData.health_predictions.malaria.risk_level) :
                                        <Chip label="UNKNOWN" color="default" size="small" />
                                    }
                                    <Typography variant="caption" display="block">
                                      Confidence: {Math.round(
                                        (riskData.risk_prediction?.malaria?.probability || 
                                         riskData.health_predictions?.malaria?.probability || 0) * 100
                                      )}%
                                    </Typography>
                                  </CardContent>
                                </Card>
                              </Grid>
                              <Grid item xs={6} md={3}>
                                <Card variant="outlined">
                                  <CardContent>
                                    <Typography variant="subtitle1">Heatstroke</Typography>
                                    {riskData.risk_prediction?.heatstroke?.risk_level ? 
                                      renderRiskLevel(riskData.risk_prediction.heatstroke.risk_level) :
                                      riskData.health_predictions?.heatstroke?.risk_level ? 
                                        renderRiskLevel(riskData.health_predictions.heatstroke.risk_level) :
                                        <Chip label="UNKNOWN" color="default" size="small" />
                                    }
                                    <Typography variant="caption" display="block">
                                      Confidence: {Math.round(
                                        (riskData.risk_prediction?.heatstroke?.probability || 
                                         riskData.health_predictions?.heatstroke?.probability || 0) * 100
                                      )}%
                                    </Typography>
                                  </CardContent>
                                </Card>
                              </Grid>
                              <Grid item xs={6} md={3}>
                                <Card variant="outlined">
                                  <CardContent>
                                    <Typography variant="subtitle1">Diarrhea</Typography>
                                    {riskData.risk_prediction?.diarrhea?.risk_level ? 
                                      renderRiskLevel(riskData.risk_prediction.diarrhea.risk_level) :
                                      riskData.health_predictions?.diarrhea?.risk_level ? 
                                        renderRiskLevel(riskData.health_predictions.diarrhea.risk_level) :
                                        <Chip label="UNKNOWN" color="default" size="small" />
                                    }
                                    <Typography variant="caption" display="block">
                                      Confidence: {Math.round(
                                        (riskData.risk_prediction?.diarrhea?.probability || 
                                         riskData.health_predictions?.diarrhea?.probability || 0) * 100
                                      )}%
                                    </Typography>
                                  </CardContent>
                                </Card>
                              </Grid>
                            </Grid>
                            <Box sx={{ mt: 2 }}>
                              <Typography variant="subtitle1">Overall Risk Assessment:</Typography>
                              {riskData.risk_prediction?.overall?.risk_level ? 
                                renderRiskLevel(riskData.risk_prediction.overall.risk_level) :
                                riskData.health_predictions?.overall?.risk_level ? 
                                  renderRiskLevel(riskData.health_predictions.overall.risk_level) :
                                  <Chip label="UNKNOWN" color="default" size="small" />
                              }
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    </Grid>
                  ) : (
                    <Alert severity="info">
                      No risk data available for this location
                    </Alert>
                  )}
                </Box>
              )}

              {/* Resource Needs Tab */}
              {tab === 1 && (
                <Box>
                  {isLoading.resources ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                      <CircularProgress />
                    </Box>
                  ) : resourceData ? (
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <Card>
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              Current Resources
                            </Typography>
                            <Grid container spacing={2}>
                              <Grid item xs={6}>
                                <Typography>
                                  Beds: {resourceData.current_resources.beds}
                                </Typography>
                                <Typography>
                                  Doctors: {resourceData.current_resources.doctors}
                                </Typography>
                                <Typography>
                                  Nurses: {resourceData.current_resources.nurses}
                                </Typography>
                              </Grid>
                              <Grid item xs={6}>
                                <Typography>
                                  IV Fluids: {resourceData.current_resources.iv_fluids}
                                </Typography>
                                <Typography>
                                  Antibiotics: {resourceData.current_resources.antibiotics}
                                </Typography>
                                <Typography>
                                  Antipyretics: {resourceData.current_resources.antipyretics}
                                </Typography>
                              </Grid>
                            </Grid>
                          </CardContent>
                        </Card>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Card>
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              Predicted Needs
                            </Typography>
                            <Grid container spacing={2}>
                              <Grid item xs={6}>
                                <Typography>
                                  Beds: {resourceData.predicted_resources.beds}
                                </Typography>
                                <Typography>
                                  Doctors: {resourceData.predicted_resources.doctors}
                                </Typography>
                                <Typography>
                                  Nurses: {resourceData.predicted_resources.nurses}
                                </Typography>
                              </Grid>
                              <Grid item xs={6}>
                                <Typography>
                                  IV Fluids: {resourceData.predicted_resources.iv_fluids}
                                </Typography>
                                <Typography>
                                  Antibiotics: {resourceData.predicted_resources.antibiotics}
                                </Typography>
                                <Typography>
                                  Antipyretics: {resourceData.predicted_resources.antipyretics}
                                </Typography>
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
                            {resourceData.recommendations.length === 0 ? (
                              <Alert severity="success">
                                Current resources are sufficient for predicted health needs
                              </Alert>
                            ) : (
                              resourceData.recommendations.map((rec: any, idx: number) => (
                                <Alert severity="warning" key={idx} sx={{ mt: 1 }}>
                                  <AlertTitle>{rec.resource.toUpperCase()}</AlertTitle>
                                  {rec.message}
                                </Alert>
                              ))
                            )}
                          </CardContent>
                        </Card>
                      </Grid>
                    </Grid>
                  ) : (
                    <Alert severity="info">
                      No resource data available for this location
                    </Alert>
                  )}
                </Box>
              )}
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default Dashboard;
