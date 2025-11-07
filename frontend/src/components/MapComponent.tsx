import React, { useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { Feature } from 'geojson';

// Fix Leaflet's default icon issue will be done inside the component

// Component to set the map view
const SetMapView = ({ center, zoom }: { center: [number, number]; zoom: number }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
};

interface MapComponentProps {
  geoJson: any;
  style: (feature: any) => L.PathOptions;
  onEachFeature: (feature: Feature, layer: L.Layer) => void;
}

const MapComponent: React.FC<MapComponentProps> = ({ geoJson, style, onEachFeature }) => {
  // Fix Leaflet's default icon issue
  useEffect(() => {
    // This code only runs on the client
    delete (L.Icon.Default.prototype as any)._getIconUrl;
    (L.Icon.Default as any).mergeOptions({
      iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
      iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
    });
  }, []);
  
  return (
    <MapContainer
      center={[23.5937, 78.9629]} // Center of India
      zoom={4}
      style={{ height: '100%', minHeight: '400px', width: '100%' }}
      scrollWheelZoom={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {geoJson && (
        <GeoJSON 
          data={geoJson} 
          style={style as any} 
          onEachFeature={onEachFeature}
        />
      )}
      <SetMapView center={[23.5937, 78.9629]} zoom={4} />
    </MapContainer>
  );
};

export default MapComponent;
