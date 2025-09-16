type Props = { alerts: string[] };

export default function AlertsList({ alerts }: Props) {
  return (
    <div className="card p-6">
      <h3 className="font-semibold mb-2">Alerts</h3>
      <ul className="list-disc pl-5 text-sm text-gray-700">
        {alerts.map((a, i) => (
          <li key={i}>{a}</li>
        ))}
      </ul>
    </div>
  );
}


