type Props = { risk: number };

export default function RiskScore({ risk }: Props) {
  const color = risk > 0.7 ? "text-red-600" : risk >= 0.5 ? "text-yellow-600" : "text-green-600";
  return (
    <div className="card p-6 text-center">
      <div className={`text-4xl font-bold ${color}`}>Risk: {risk.toFixed(2)}</div>
      <div className="text-sm text-gray-600">Heat stress risk score (mock)</div>
    </div>
  );
}


