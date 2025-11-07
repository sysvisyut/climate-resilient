import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, CircularProgress, Button, ToggleButtonGroup, ToggleButton } from '@mui/material';
import { getDataSummary } from '../utils/api';
import { Feature, FeatureCollection } from 'geojson';
import dynamic from 'next/dynamic';

// Dynamically import Leaflet components with no SSR
const MapWithNoSSR = dynamic(
  () => import('./MapComponent'), 
  { 
    ssr: false,
    loading: () => (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>Loading map...</Typography>
      </Box>
    )
  }
);

// GeoJSON data for India states
const INDIA_STATES_URL = 'https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson';

// Define the props interface
interface IndiaMapProps {
  colorBy: 'dengue' | 'malaria' | 'heatstroke' | 'diarrhea' | 'overall';
  onLocationClick: (locationId: number, locationName: string) => void;
}

// Define the location data interface
interface LocationData {
  location_id: number;
  name: string;
  type: string;
  population: number;
  dengue_cases: number;
  dengue_rate: number;
  malaria_cases: number;
  malaria_rate: number;
  heatstroke_cases: number;
  heatstroke_rate: number;
  diarrhea_cases: number;
  diarrhea_rate: number;
  overall_burden: number;
  dengue_risk_level?: string;
  malaria_risk_level?: string;
  heatstroke_risk_level?: string;
  diarrhea_risk_level?: string;
  overall_risk_level?: string;
  risk_predictions?: any;
  available_beds?: number;
  total_beds?: number;
}

// SetMapView component is now in MapComponent.tsx

const IndiaLeafletMap: React.FC<IndiaMapProps> = ({ colorBy, onLocationClick }) => {
  const [data, setData] = useState<LocationData[]>([]);
  const [geoJson, setGeoJson] = useState<FeatureCollection | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState<'rates' | 'risk_levels'>('risk_levels');

  // Fetch GeoJSON data for India states
  useEffect(() => {
    const fetchGeoJson = async () => {
      try {
        const response = await fetch(INDIA_STATES_URL);
        if (!response.ok) {
          throw new Error(`Failed to fetch GeoJSON: ${response.status}`);
        }
        const data = await response.json();
        setGeoJson(data);
      } catch (err) {
        console.error('Error fetching GeoJSON:', err);
        setError('Failed to load map data. Please check your internet connection.');
      }
    };

    fetchGeoJson();
  }, []);

  // Fetch health data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const summaryData = await getDataSummary();

        if (!summaryData || !summaryData.locations || !Array.isArray(summaryData.locations) || summaryData.locations.length === 0) {
          console.error('Invalid or empty data returned from API:', summaryData);
          setError('No location data available. Please ensure the backend is properly initialized.');
          setIsLoading(false);
          return;
        }

        console.log('Loaded data for map:', summaryData.locations.length, 'locations');
        setData(summaryData.locations);
        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching data for map:', err);
        setError('Failed to load map data. Please check the backend connection.');
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  // Get color based on value and view mode
  const getColor = (locationName: string): string => {
    if (!data || data.length === 0) return '#CCCCCC'; // Default gray

    const locationData = data.find(loc => loc.name === locationName);
    if (!locationData) return '#CCCCCC';

    if (viewMode === 'risk_levels') {
      const riskLevel = locationData[`${colorBy}_risk_level`] || 'unknown';
      
      // Color based on risk level
      switch (riskLevel) {
        case 'low': return '#66BB6A'; // Green
        case 'medium': return '#FFA726'; // Orange
        case 'high': return '#EF5350'; // Red
        case 'critical': return '#7B1FA2'; // Purple
        default: return '#CCCCCC'; // Gray for unknown
      }
    } else {
      // Color based on rate values
      let value = 0;
      switch (colorBy) {
        case 'dengue': value = locationData.dengue_rate || 0; break;
        case 'malaria': value = locationData.malaria_rate || 0; break;
        case 'heatstroke': value = locationData.heatstroke_rate || 0; break;
        case 'diarrhea': value = locationData.diarrhea_rate || 0; break;
        case 'overall': value = locationData.overall_burden || 0; break;
      }

      // Color gradient based on value
      if (value > 100) return '#7B1FA2'; // Purple for very high
      if (value > 50) return '#EF5350'; // Red for high
      if (value > 20) return '#FFA726'; // Orange for medium
      if (value > 5) return '#FFEE58'; // Yellow for low-medium
      return '#66BB6A'; // Green for low
    }
  };

  // Style function for GeoJSON
  const style = (feature: Feature) => {
    const stateName = feature.properties?.NAME_1 || feature.properties?.name;
    return {
      fillColor: getColor(stateName),
      weight: 1,
      opacity: 1,
      color: '#666',
      fillOpacity: 0.7
    };
  };

  // Get tooltip content
  const getTooltipContent = (feature: Feature) => {
    const stateName = feature.properties?.NAME_1 || feature.properties?.name;
    const locationData = data.find(loc => loc.name === stateName);
    
    if (!locationData) {
      return `<b>${stateName}</b><br/>No data available`;
    }

    let content = `<b>${stateName}</b><br/>`;
    
    if (viewMode === 'risk_levels') {
      content += `${colorBy.charAt(0).toUpperCase() + colorBy.slice(1)} Risk: ${locationData[`${colorBy}_risk_level`] || 'Unknown'}<br/>`;
      
      // Add more details if available
      const riskPredictions = locationData.risk_predictions?.[colorBy];
      if (riskPredictions) {
        content += `Probability: ${(riskPredictions.probability * 100).toFixed(1)}%<br/>`;
      }
    } else {
      let rate = 0;
      switch (colorBy) {
        case 'dengue': rate = locationData.dengue_rate || 0; break;
        case 'malaria': rate = locationData.malaria_rate || 0; break;
        case 'heatstroke': rate = locationData.heatstroke_rate || 0; break;
        case 'diarrhea': rate = locationData.diarrhea_rate || 0; break;
        case 'overall': rate = locationData.overall_burden || 0; break;
      }
      content += `${colorBy.charAt(0).toUpperCase() + colorBy.slice(1)} Rate: ${rate.toFixed(2)} per 100k<br/>`;
      if (colorBy !== 'overall') {
        let cases = 0;
        switch (colorBy) {
          case 'dengue': cases = locationData.dengue_cases || 0; break;
          case 'malaria': cases = locationData.malaria_cases || 0; break;
          case 'heatstroke': cases = locationData.heatstroke_cases || 0; break;
          case 'diarrhea': cases = locationData.diarrhea_cases || 0; break;
        }
        content += `Cases: ${cases}<br/>`;
      }
    }

    // Add hospital data if available
    if (locationData.available_beds !== undefined && locationData.total_beds !== undefined) {
      content += `Hospital Beds: ${locationData.available_beds} available / ${locationData.total_beds} total<br/>`;
    }

    return content;
  };

  // Handle click on a state
  const onEachFeature = (feature: Feature, layer: L.Layer) => {
    const stateName = feature.properties?.NAME_1 || feature.properties?.name;
    const locationData = data.find(loc => loc.name === stateName);
    
    if (locationData) {
      layer.on({
        click: () => {
          console.log('Leaflet map: clicked on state:', stateName, 'with ID:', locationData.location_id);
          onLocationClick(locationData.location_id, stateName);
        }
      });
    }

    layer.bindTooltip(() => getTooltipContent(feature), { 
      sticky: true,
      direction: 'top'
    });
  };

  const handleViewModeChange = (_event: React.MouseEvent<HTMLElement>, newMode: 'rates' | 'risk_levels' | null) => {
    if (newMode !== null) {
      setViewMode(newMode);
    }
  };

  const getMapTitle = () => {
    const disease = colorBy.charAt(0).toUpperCase() + colorBy.slice(1);
    return viewMode === 'risk_levels' 
      ? `${disease} Risk Levels Across India` 
      : `${disease} Case Rates Across India (per 100k)`;
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>Loading map data...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2, border: '1px solid #f44336', borderRadius: 1, bgcolor: '#ffebee' }}>
        <Typography color="error" variant="h6">Error Loading Map</Typography>
        <Typography color="error">{error}</Typography>
        <Button
          variant="contained"
          color="primary"
          sx={{ mt: 2 }}
          onClick={() => window.location.reload()}
        >
          Retry
        </Button>
      </Box>
    );
  }

  if (!geoJson) {
    return (
      <Box sx={{ p: 2, border: '1px solid #ff9800', borderRadius: 1, bgcolor: '#fff3e0' }}>
        <Typography color="warning" variant="h6">Loading Map Data</Typography>
        <Typography>The map data is still loading. Please wait...</Typography>
        <CircularProgress sx={{ mt: 2 }} />
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" align="center" gutterBottom>
        {getMapTitle()}
      </Typography>
      
      <Box sx={{ mb: 1, display: 'flex', justifyContent: 'center' }}>
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
      </Box>
      
      <Box sx={{ flexGrow: 1, minHeight: '400px', border: '1px solid #ccc', borderRadius: 1 }}>
        {typeof window !== 'undefined' && geoJson && (
          <MapWithNoSSR 
            geoJson={geoJson}
            style={style}
            onEachFeature={onEachFeature}
          />
        )}
      </Box>
      
      <Box sx={{ mt: 2 }}>
        <Paper elevation={1} sx={{ p: 1 }}>
          <Typography variant="subtitle2" gutterBottom>Risk Level Legend:</Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box sx={{ width: 16, height: 16, bgcolor: '#66BB6A', mr: 1 }}></Box>
              <Typography variant="body2">Low</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box sx={{ width: 16, height: 16, bgcolor: '#FFA726', mr: 1 }}></Box>
              <Typography variant="body2">Medium</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box sx={{ width: 16, height: 16, bgcolor: '#EF5350', mr: 1 }}></Box>
              <Typography variant="body2">High</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box sx={{ width: 16, height: 16, bgcolor: '#7B1FA2', mr: 1 }}></Box>
              <Typography variant="body2">Critical</Typography>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Box>
  );
};

export default IndiaLeafletMap;
