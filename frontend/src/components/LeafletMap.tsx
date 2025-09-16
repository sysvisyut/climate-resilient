"use client";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect } from "react";

type Props = { coords: [number, number]; risk: number; region: string };

export default function LeafletMap({ coords, risk, region }: Props) {
  useEffect(() => {
    // Fix default icon path
    // @ts-ignore
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
      iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
      shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    });
  }, []);

  const color = risk > 0.7 ? "#dc2626" : risk >= 0.5 ? "#ca8a04" : "#16a34a";

  return (
    <MapContainer center={coords} zoom={10} scrollWheelZoom={false} className="h-full w-full" aria-label="Risk map">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Marker position={coords}>
        <Popup>
          <div>
            <div className="font-semibold">{region}</div>
            <div style={{ color }}>Risk: {risk}</div>
          </div>
        </Popup>
      </Marker>
    </MapContainer>
  );
}


