"use client";
import dynamic from "next/dynamic";
import "leaflet/dist/leaflet.css";

type Props = { coords: [number, number]; risk: number; region: string };

const LeafletMap = dynamic(() => import("@/components/LeafletMap"), { ssr: false });

export default function RiskMap({ coords, risk, region }: Props) {
  // No-op: handled in LeafletMap

  const color = risk > 0.7 ? "#dc2626" : risk >= 0.5 ? "#ca8a04" : "#16a34a";

  return (
    <div className="card p-0 overflow-hidden">
      <div className="p-4"><h3 className="font-semibold">Risk Map</h3></div>
      <div className="h-72">
        <LeafletMap coords={coords} risk={risk} region={region} />
      </div>
    </div>
  );
}


