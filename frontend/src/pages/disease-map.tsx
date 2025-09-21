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
  ToggleButtonGroup,
  ToggleButton,
  Button
} from '@mui/material';
import Layout from '../components/Layout';
import { isAuthenticated } from '../utils/auth';
import { getDataSummary, getLocations } from '../utils/api';
import dynamic from 'next/dynamic';

// Import icons
import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety';
import CoronavirusIcon from '@mui/icons-material/Coronavirus';
import WbSunnyIcon from '@mui/icons-material/WbSunny';
import WaterDropIcon from '@mui/icons-material/WaterDrop';

// Dynamically import the Leaflet map component with no SSR
const DiseaseMapWithNoSSR = dynamic(
  () => import('../components/DiseaseMap'),
  { 
    ssr: false,
    loading: () => (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px' }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>Loading map...</Typography>
      </Box>
    )
  }
);

export default function DiseaseMapPage() {
  const router = useRouter();
  const [mapData, setMapData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [mapColorBy, setMapColorBy] = useState<'overall' | 'dengue' | 'malaria' | 'heatstroke' | 'diarrhea'>('overall');
  const [viewMode, setViewMode] = useState<'rates' | 'risk_levels'>('risk_levels');
  const [selectedLocation, setSelectedLocation] = useState<any>(null);
  const [locations, setLocations] = useState<any[]>([]);

  useEffect(() => {
    // Check if user is authenticated
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    // Fetch data for the map
    const fetchMapData = async () => {
      try {
        setIsLoading(true);
        const summaryData = await getDataSummary();
        
        if (!summaryData || !summaryData.locations || !Array.isArray(summaryData.locations)) {
          setError('No data available. Please ensure the backend is properly initialized.');
          setIsLoading(false);
          return;
        }
        
        console.log('Loaded data for map:', summaryData.locations.length, 'locations');
        setMapData(summaryData.locations);
        
        // Also fetch locations for the dropdown
        const locationsData = await getLocations();
        setLocations(locationsData);
        
        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching map data:', err);
        setError('Failed to load map data. Please check the backend connection.');
        setIsLoading(false);
      }
    };

    fetchMapData();
  }, [router]);

  const handleLocationSelect = (locationId: number, locationName: string) => {
    console.log('Location selected:', locationId, locationName);
    setSelectedLocation({ id: locationId, name: locationName });
    
    // Navigate to dashboard with the selected location
    router.push({
      pathname: '/admin/dashboard',
      query: { locationId, locationName }
    });
  };

  const handleViewModeChange = (_event: React.MouseEvent<HTMLElement>, newMode: 'rates' | 'risk_levels' | null) => {
    if (newMode !== null) {
      setViewMode(newMode);
    }
  };

  const handleDropdownChange = (event: any) => {
    const locationId = event.target.value;
    const location = locations.find(loc => loc.id === locationId);
    if (location) {
      handleLocationSelect(locationId, location.name);
    }
  };

  return (
    <Layout title="Disease Map">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Disease Risk Map
        </Typography>
        <Typography variant="body1">
          Interactive map showing health risks across India based on real-time climate data.
        </Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <Typography variant="h6" gutterBottom>
              Select Disease Category
            </Typography>
            <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
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
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h6" gutterBottom>
              View Mode
            </Typography>
            <ToggleButtonGroup
              value={viewMode}
              exclusive
              onChange={handleViewModeChange}
              aria-label="view mode"
              size="small"
            >
              <ToggleButton value="risk_levels" aria-label="risk levels">
                Risk Levels
              </ToggleButton>
              <ToggleButton value="rates" aria-label="case rates">
                Case Rates
              </ToggleButton>
            </ToggleButtonGroup>
          </Grid>
        </Grid>
      </Paper>

      <Paper elevation={3} sx={{ p: 3 }}>
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel id="location-select-label">Select Location</InputLabel>
          <Select
            labelId="location-select-label"
            value={selectedLocation?.id || ''}
            onChange={handleDropdownChange}
            label="Select Location"
            disabled={isLoading}
          >
            {locations.map((location) => (
              <MenuItem key={location.id} value={location.id}>
                {location.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4, height: '500px' }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        ) : (
          <Box sx={{ height: '600px', width: '100%' }}>
            <DiseaseMapWithNoSSR 
              data={mapData} 
              colorBy={mapColorBy} 
              viewMode={viewMode}
              onLocationClick={handleLocationSelect} 
            />
          </Box>
        )}

        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Map Legend
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6} md={3}>
              <Paper elevation={1} sx={{ p: 1, bgcolor: '#66BB6A' }}>
                <Typography variant="body2" align="center" sx={{ color: 'white' }}>
                  Low Risk
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={6} md={3}>
              <Paper elevation={1} sx={{ p: 1, bgcolor: '#FFA726' }}>
                <Typography variant="body2" align="center" sx={{ color: 'white' }}>
                  Medium Risk
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={6} md={3}>
              <Paper elevation={1} sx={{ p: 1, bgcolor: '#EF5350' }}>
                <Typography variant="body2" align="center" sx={{ color: 'white' }}>
                  High Risk
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={6} md={3}>
              <Paper elevation={1} sx={{ p: 1, bgcolor: '#7B1FA2' }}>
                <Typography variant="body2" align="center" sx={{ color: 'white' }}>
                  Critical Risk
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Layout>
  );
}