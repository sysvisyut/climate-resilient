import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { Box, Typography, CircularProgress, Chip } from '@mui/material';
import { Feature, FeatureCollection } from 'geojson';

// Fix Leaflet's default icon issue
const DefaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// GeoJSON data for India states
const INDIA_STATES_URL = 'https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson';

// Component to set the map view
const SetMapView = ({ center, zoom }: { center: [number, number]; zoom: number }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
};

interface DiseaseMapProps {
  data: any[];
  colorBy: 'dengue' | 'malaria' | 'heatstroke' | 'diarrhea' | 'overall';
  viewMode: 'rates' | 'risk_levels';
  onLocationClick: (locationId: number, locationName: string) => void;
}

const DiseaseMap: React.FC<DiseaseMapProps> = ({ data, colorBy, viewMode, onLocationClick }) => {
  const [geoJson, setGeoJson] = useState<FeatureCollection | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Fix Leaflet's default icon issue
  useEffect(() => {
    // This code only runs on the client; cast to any to access private leaflet property
    delete (L.Icon.Default.prototype as any)._getIconUrl;
    (L.Icon.Default as any).mergeOptions({
      iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
      iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
    });
  }, []);

  // Fetch GeoJSON data for India states
  useEffect(() => {
    const fetchGeoJson = async () => {
      try {
        const response = await fetch(INDIA_STATES_URL);
        if (!response.ok) {
          throw new Error(`Failed to fetch GeoJSON: ${response.status}`);
        }
        const jsonData = await response.json();
        setGeoJson(jsonData);
        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching GeoJSON:', err);
        setError('Failed to load map data. Please check your internet connection.');
        setIsLoading(false);
      }
    };

    fetchGeoJson();
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
  const style = (feature: any): L.PathOptions => {
    const stateName = feature?.properties?.NAME_1 || feature?.properties?.name;
    return {
      fillColor: getColor(stateName),
      weight: 1,
      opacity: 1,
      color: '#666',
      fillOpacity: 0.7
    };
  };

  // Create popup content
  const createPopupContent = (feature: Feature) => {
    const stateName = feature.properties?.NAME_1 || feature.properties?.name;
    const locationData = data.find(loc => loc.name === stateName);
    
    if (!locationData) {
      return `<div><strong>${stateName}</strong><br/>No data available</div>`;
    }

    const diseaseName = colorBy.charAt(0).toUpperCase() + colorBy.slice(1);
    let content = `<div style="min-width: 200px;">
      <h3 style="margin-top: 0;">${stateName}</h3>
      <p><strong>${diseaseName} Risk:</strong> ${locationData[`${colorBy}_risk_level`] || 'Unknown'}</p>`;
    
    // Add more details based on the disease
    const riskPredictions = locationData.risk_predictions?.[colorBy];
    if (riskPredictions) {
      content += `<p><strong>Probability:</strong> ${(riskPredictions.probability * 100).toFixed(1)}%</p>`;
      if (riskPredictions.rate_per_100k) {
        content += `<p><strong>Rate:</strong> ${riskPredictions.rate_per_100k.toFixed(2)} per 100k</p>`;
      }
    }
    
    // Add climate data if available
    if (locationData.temperature !== undefined) {
      content += `<hr style="margin: 10px 0;" />
      <p><strong>Current Weather:</strong></p>
      <p>Temperature: ${locationData.temperature}°C</p>
      <p>Humidity: ${locationData.humidity}%</p>`;
    }
    
    content += `<hr style="margin: 10px 0;" />
      <p style="text-align: center; margin-bottom: 0;">
        <em>Click for detailed analysis</em>
      </p>
    </div>`;
    
    return content;
  };

  // Handle click on a state
  const onEachFeature = (feature: Feature, layer: L.Layer) => {
    const stateName = feature.properties?.NAME_1 || feature.properties?.name;
    const locationData = data.find(loc => loc.name === stateName);
    
    // Create popup
    const popupContent = createPopupContent(feature);
    const popup = L.popup().setContent(popupContent);
    layer.bindPopup(popup);
    
    if (locationData) {
      layer.on({
        click: () => {
          console.log('Disease Map: clicked on state:', stateName, 'with ID:', locationData.location_id);
          onLocationClick(locationData.location_id, stateName);
        }
      });
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>Loading map data...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2, border: '1px solid #f44336', borderRadius: 1, bgcolor: '#ffebee', height: '100%' }}>
        <Typography color="error" variant="h6">Error Loading Map</Typography>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', width: '100%' }}>
      <MapContainer
        center={[23.5937, 78.9629]} // Center of India
        zoom={4}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {geoJson && (
          <GeoJSON 
            data={geoJson} 
            style={style} 
            onEachFeature={onEachFeature}
          />
        )}
        <SetMapView center={[23.5937, 78.9629]} zoom={4} />
      </MapContainer>
    </Box>
  );
};

export default DiseaseMap;
