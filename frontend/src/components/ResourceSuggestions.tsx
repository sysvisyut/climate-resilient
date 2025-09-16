type Props = { risk: number };

export default function ResourceSuggestions({ risk }: Props) {
  const suggestBeds = risk > 0.7 ? 10 : risk > 0.5 ? 5 : 2;
  const suggestStaff = risk > 0.7 ? 5 : risk > 0.5 ? 3 : 1;
  return (
    <div className="card p-6">
      <h3 className="font-semibold mb-2">Resource Suggestions</h3>
      <ul className="list-disc pl-5 text-sm text-gray-700">
        <li>{suggestBeds} hospital beds</li>
        <li>{suggestStaff} additional staff</li>
      </ul>
      <p className="text-xs text-gray-500 mt-2">Calculated from mock risk thresholds</p>
    </div>
  );
}


