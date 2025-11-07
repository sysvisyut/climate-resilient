import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { Box, Paper, Typography, Grid, Card, CardContent, Alert, FormControl, InputLabel, Select, MenuItem, CircularProgress } from '@mui/material';
import dynamic from 'next/dynamic';
import Layout from '../components/Layout';
import { isAuthenticated, getUserLocationId } from '../utils/auth';
import { getLocations, forecastDiseases } from '../utils/api';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), {
  ssr: false,
  loading: () => <CircularProgress />,
});

export default function ForecastsPage() {
  const router = useRouter();
  const [locations, setLocations] = useState<any[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<number | null>(null);
  const [forecastData, setForecastData] = useState<any>(null);
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
          fetchForecastData(userLocationId);
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

  const fetchForecastData = async (locationId: number) => {
    try {
      setIsLoading(true);
      const data = await forecastDiseases(locationId, 14); // 14 days forecast
      setForecastData(data);
      setIsLoading(false);
    } catch (err) {
      console.error('Error fetching forecast data:', err);
      setError('Failed to load forecast data');
      setIsLoading(false);
    }
  };

  const handleLocationChange = (event: any) => {
    const locationId = Number(event.target.value);
    console.log('Selected location ID:', locationId);
    setSelectedLocation(locationId);
    fetchForecastData(locationId);
  };

  const renderForecastChart = (disasterType: string) => {
    if (!forecastData || !forecastData.forecast_disasters || forecastData.forecast_disasters.length === 0) {
      return (
        <Box sx={{ p: 2, textAlign: 'center' }}>
          <Typography color="text.secondary">No forecast data available</Typography>
        </Box>
      );
    }
    
    // Extract data for the chart from the enhanced prediction model
    const dates = forecastData.forecast_disasters.map((f: any) => f.date);
    
    // Get probabilities for the disaster type
    const probabilities = forecastData.forecast_disasters.map((f: any) => 
      f.disasters[disasterType]?.probability ? Math.round(f.disasters[disasterType].probability * 100) : 0
    );
    
    // Get current probability
    const currentProbability = forecastData.current_disasters[disasterType]?.probability 
      ? Math.round(forecastData.current_disasters[disasterType].probability * 100) 
      : 0;
    
    // Get risk levels for coloring
    const riskLevels = forecastData.forecast_disasters.map((f: any) => 
      f.disasters[disasterType]?.risk_level || 'low'
    );
    
    // Map risk levels to colors
    const riskColors = riskLevels.map((level: string) => {
      switch(level) {
        case 'critical': return 'rgb(123, 31, 162)'; // Purple
        case 'high': return 'rgb(239, 83, 80)';      // Red
        case 'medium': return 'rgb(255, 167, 38)';   // Orange
        case 'low': 
        default: return 'rgb(102, 187, 106)';        // Green
      }
    });
    
    // Format disaster type name
    const disasterName = disasterType.charAt(0).toUpperCase() + disasterType.slice(1);
    
    return (
      <Plot
        data={[
          {
            x: dates,
            y: probabilities,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Forecast',
            line: { color: 'rgb(0, 100, 200)', width: 2 },
            marker: { 
              color: riskColors,
              size: 8
            }
          },
          {
            x: [forecastData.current_date],
            y: [currentProbability],
            type: 'scatter',
            mode: 'markers',
            name: 'Current',
            marker: { 
              color: getColorForRiskLevel(forecastData.current_disasters[disasterType]?.risk_level || 'low'),
              size: 12,
              symbol: 'star'
            }
          }
        ]}
        layout={{
          title: { text: `${disasterName} Risk Forecast` },
          xaxis: { title: { text: 'Date' } },
          yaxis: { 
            title: { text: 'Risk Probability (%)' },
            range: [0, 100]
          },
          autosize: true,
          height: 350,
          margin: { l: 50, r: 20, t: 40, b: 50 }
        }}
        style={{ width: '100%' }}
        config={{ responsive: true }}
      />
    );
  };
  
  const getColorForRiskLevel = (level: string): string => {
    switch(level) {
      case 'critical': return 'rgb(123, 31, 162)'; // Purple
      case 'high': return 'rgb(239, 83, 80)';      // Red
      case 'medium': return 'rgb(255, 167, 38)';   // Orange
      case 'low': 
      default: return 'rgb(102, 187, 106)';        // Green
    }
  };

  return (
    <Layout title="Natural Disaster Forecasts">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Natural Disaster Forecasts
        </Typography>
        <Typography variant="body1">
          Real-time predictions of natural disaster risks for the next 5 days based on current weather data.
        </Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
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
          <Alert severity="info">Please select a location to view forecasts</Alert>
        ) : isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : forecastData ? (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              {renderForecastChart('flood')}
            </Grid>
            <Grid item xs={12} md={6}>
              {renderForecastChart('cyclone')}
            </Grid>
            <Grid item xs={12} md={6}>
              {renderForecastChart('heatwave')}
            </Grid>
            <Grid item xs={12} md={6}>
              {renderForecastChart('landslide')}
            </Grid>
            <Grid item xs={12} md={6}>
              {renderForecastChart('drought')}
            </Grid>
          </Grid>
        ) : null}
      </Paper>
    </Layout>
  );
}
