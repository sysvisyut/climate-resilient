import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Box, CircularProgress, Typography, Tooltip, Button, ButtonGroup } from '@mui/material';
import { getDataSummary } from '../utils/api';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), {
  ssr: false,
  loading: () => <CircularProgress />,
});

interface RiskData {
  risk_level: string;
  probability: number;
  rate_per_100k?: number;
}

interface LocationData {
  location_id: number;
  name: string;
  type: string;
  temperature: number;
  rainfall: number;
  humidity: number;
  dengue_cases: number;
  dengue_rate: number;
  dengue_risk_level: string;
  malaria_cases: number;
  malaria_rate: number;
  malaria_risk_level: string;
  heatstroke_cases: number;
  heatstroke_rate: number;
  heatstroke_risk_level: string;
  diarrhea_cases: number;
  diarrhea_rate: number;
  diarrhea_risk_level: string;
  overall_disease_burden: number;
  overall_risk_level: string;
  risk_predictions: {
    [disease: string]: RiskData;
  };
  total_beds: number;
  available_beds: number;
  bed_occupancy_rate: number;
}

interface IndiaMapProps {
  colorBy: 'dengue' | 'malaria' | 'heatstroke' | 'diarrhea' | 'overall';
  onLocationClick: (locationId: number, locationName: string) => void;
}

const IndiaMap = ({ colorBy, onLocationClick }: IndiaMapProps) => {
  const [data, setData] = useState<LocationData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState<'rates' | 'risk_levels'>('risk_levels');

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

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
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
  
  if (!data || data.length === 0) {
    return (
      <Box sx={{ p: 2, border: '1px solid #ff9800', borderRadius: 1, bgcolor: '#fff3e0' }}>
        <Typography color="warning" variant="h6">No Data Available</Typography>
        <Typography>No location data is available to display on the map. Please ensure the backend is properly initialized.</Typography>
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

  // Map risk levels to numerical values for choropleth
  const riskLevelToValue = {
    'low': 1,
    'medium': 2,
    'high': 3,
    'critical': 4,
    'unknown': 0
  };

  // Determine values to use for coloring based on view mode
  const getColorValues = () => {
    if (viewMode === 'rates') {
      // Use rates (numeric values)
      if (colorBy === 'dengue') {
        return data.map((loc) => loc.dengue_rate);
      } else if (colorBy === 'malaria') {
        return data.map((loc) => loc.malaria_rate);
      } else if (colorBy === 'heatstroke') {
        return data.map((loc) => loc.heatstroke_rate);
      } else if (colorBy === 'diarrhea') {
        return data.map((loc) => loc.diarrhea_rate);
      } else {
        return data.map((loc) => loc.overall_disease_burden);
      }
    } else {
      // Use risk levels (categorical converted to numeric for visualization)
      if (colorBy === 'dengue') {
        return data.map((loc) => riskLevelToValue[(loc.dengue_risk_level || 'unknown') as keyof typeof riskLevelToValue]);
      } else if (colorBy === 'malaria') {
        return data.map((loc) => riskLevelToValue[(loc.malaria_risk_level || 'unknown') as keyof typeof riskLevelToValue]);
      } else if (colorBy === 'heatstroke') {
        return data.map((loc) => riskLevelToValue[(loc.heatstroke_risk_level || 'unknown') as keyof typeof riskLevelToValue]);
      } else if (colorBy === 'diarrhea') {
        return data.map((loc) => riskLevelToValue[(loc.diarrhea_risk_level || 'unknown') as keyof typeof riskLevelToValue]);
      } else {
        return data.map((loc) => riskLevelToValue[(loc.overall_risk_level || 'unknown') as keyof typeof riskLevelToValue]);
      }
    }
  };

  // Determine color scale based on disease and view mode
  const getColorScale = () => {
    if (viewMode === 'risk_levels') {
      // Risk level color scale (consistent across all diseases)
      return [
        [0, 'rgb(200, 200, 200)'],  // unknown - gray
        [0.2, 'rgb(120, 220, 120)'], // low - green
        [0.4, 'rgb(255, 255, 0)'],   // medium - yellow
        [0.6, 'rgb(255, 140, 0)'],   // high - orange
        [0.8, 'rgb(255, 0, 0)']      // critical - red
      ];
    } else {
      // Disease-specific color scales for rates
      switch (colorBy) {
        case 'dengue':
          return [
            [0, 'rgb(255, 255, 230)'],
            [0.5, 'rgb(255, 140, 0)'],
            [1, 'rgb(178, 34, 34)'],
          ];
        case 'malaria':
          return [
            [0, 'rgb(240, 255, 240)'],
            [0.5, 'rgb(0, 128, 0)'],
            [1, 'rgb(0, 64, 0)'],
          ];
        case 'heatstroke':
          return [
            [0, 'rgb(255, 255, 200)'],
            [0.5, 'rgb(255, 170, 0)'],
            [1, 'rgb(255, 0, 0)'],
          ];
        case 'diarrhea':
          return [
            [0, 'rgb(240, 240, 255)'],
            [0.5, 'rgb(0, 170, 255)'],
            [1, 'rgb(0, 0, 128)'],
          ];
        default:
          return [
            [0, 'rgb(240, 240, 240)'],
            [0.5, 'rgb(255, 200, 0)'],
            [1, 'rgb(255, 0, 0)'],
          ];
      }
    }
  };

  // Get color bar title based on view mode
  const getColorBarTitle = () => {
    if (viewMode === 'rates') {
      return 'Cases per 100k';
    } else {
      return 'Risk Level';
    }
  };

  // Get title for the map
  const getMapTitle = () => {
    const riskOrRate = viewMode === 'rates' ? 'Rates' : 'Risk';
    switch (colorBy) {
      case 'dengue':
        return `Dengue ${riskOrRate} by State/UT`;
      case 'malaria':
        return `Malaria ${riskOrRate} by State/UT`;
      case 'heatstroke':
        return `Heatstroke ${riskOrRate} by State/UT`;
      case 'diarrhea':
        return `Diarrhea ${riskOrRate} by State/UT`;
      default:
        return `Overall Disease ${riskOrRate} by State/UT`;
    }
  };

  // Get hover text based on view mode and disease
  const getHoverText = (loc: LocationData) => {
    const riskLevel = colorBy === 'overall' 
      ? loc.overall_risk_level 
      : loc[`${colorBy}_risk_level` as keyof LocationData] as string;
      
    const rateValue = colorBy === 'overall'
      ? loc.overall_disease_burden
      : loc[`${colorBy}_rate` as keyof LocationData] as number;
    
    // Get probability from risk_predictions if available
    const probability = loc.risk_predictions?.[colorBy]?.probability 
      ? `${(loc.risk_predictions[colorBy].probability * 100).toFixed(0)}%`
      : 'N/A';
    
    return `${loc.name}<br>
      <b>Risk Level: ${riskLevel.toUpperCase()}</b><br>
      Cases: ${rateValue?.toFixed(2) || '0.00'} per 100k<br>
      Probability: ${probability}<br>
      <br>
      Climate:<br>
      Temperature: ${loc.temperature}°C<br>
      Rainfall: ${loc.rainfall}mm<br>
      Humidity: ${loc.humidity}%<br>
      <br>
      Hospital Resources:<br>
      Beds: ${loc.available_beds || 0}/${loc.total_beds || 0}<br>
      Occupancy: ${(loc.bed_occupancy_rate * 100).toFixed(1)}%`;
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
        <ButtonGroup variant="contained" color="primary">
          <Button 
            onClick={() => setViewMode('risk_levels')}
            variant={viewMode === 'risk_levels' ? 'contained' : 'outlined'}
          >
            Risk Levels
          </Button>
          <Button 
            onClick={() => setViewMode('rates')}
            variant={viewMode === 'rates' ? 'contained' : 'outlined'}
          >
            Case Rates
          </Button>
        </ButtonGroup>
      </Box>

      <Box sx={{ width: '100%', height: '600px' }}>
        <Plot
          data={[
            {
              type: 'choropleth',
              locationmode: 'country names',
              locations: data.map((loc) => loc.name),
              z: getColorValues(),
              text: data.map((loc) => getHoverText(loc)),
              colorscale: getColorScale() as any,
              colorbar: {
                title: {
                  text: getColorBarTitle(),
                  side: 'right',
                },
                thickness: 15,
                tickvals: viewMode === 'risk_levels' ? [0, 1, 2, 3, 4] : undefined,
                ticktext: viewMode === 'risk_levels' ? ['Unknown', 'Low', 'Medium', 'High', 'Critical'] : undefined,
              },
              marker: {
                line: {
                  color: 'rgb(100,100,100)',
                  width: 1,
                },
              },
              hoverinfo: 'text',
            },
          ]}
          layout={{
            title: { text: getMapTitle() },
            geo: {
              scope: 'asia',
              showlakes: true,
              lakecolor: 'rgb(200, 230, 255)',
              center: { lat: 20, lon: 78 },
              projection: { scale: 3 },
              lonaxis: { range: [68, 98] },
              lataxis: { range: [6, 38] },
            },
            autosize: true,
            margin: { l: 0, r: 0, b: 0, t: 40 },
          }}
          style={{ width: '100%', height: '100%' }}
          config={{ responsive: true }}
          onClick={(event) => {
            if (event.points && event.points[0]) {
              const locationName = (event.points[0] as any).location as string;
              console.log('Map click detected on:', locationName);
              
              const locationData = data.find((loc) => loc.name === locationName);
              if (locationData) {
                console.log('Found location data:', locationData);
                // Ensure we're passing a number for location_id
                const locationId = Number(locationData.location_id);
                if (!isNaN(locationId)) {
                  console.log('Calling onLocationClick with:', locationId, locationData.name);
                  onLocationClick(locationId, locationData.name);
                } else {
                  console.error('Invalid location ID:', locationData.location_id);
                }
              } else {
                console.error('Location data not found for:', locationName);
              }
            } else {
              console.log('Click event without valid points:', event);
            }
          }}
        />
      </Box>
      
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
        <Box sx={{ border: '1px solid #ccc', borderRadius: 1, p: 2 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>Risk Level Legend</Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 16, height: 16, backgroundColor: 'rgb(120, 220, 120)' }} />
              <Typography variant="body2">Low</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 16, height: 16, backgroundColor: 'rgb(255, 255, 0)' }} />
              <Typography variant="body2">Medium</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 16, height: 16, backgroundColor: 'rgb(255, 140, 0)' }} />
              <Typography variant="body2">High</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 16, height: 16, backgroundColor: 'rgb(255, 0, 0)' }} />
              <Typography variant="body2">Critical</Typography>
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default IndiaMap;
