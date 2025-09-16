"use client";
import { useMemo, useState } from "react";

type Patient = { name: string; risk: number; notes?: string };
type Props = { patients: Patient[]; editable?: boolean };

export default function PatientTable({ patients, editable = false }: Props) {
  const [sortKey, setSortKey] = useState<keyof Patient>("risk");
  const [sortAsc, setSortAsc] = useState(false);
  const [rows, setRows] = useState(patients);

  const sorted = useMemo(() => {
    const copy = [...rows];
    copy.sort((a, b) => {
      const va = a[sortKey] as any; const vb = b[sortKey] as any;
      if (va < vb) return sortAsc ? -1 : 1;
      if (va > vb) return sortAsc ? 1 : -1;
      return 0;
    });
    return copy;
  }, [rows, sortKey, sortAsc]);

  const toggleSort = (key: keyof Patient) => {
    if (key === sortKey) setSortAsc((v) => !v);
    else { setSortKey(key); setSortAsc(true); }
  };

  const updateNotes = (idx: number, val: string) => {
    setRows((prev) => prev.map((r, i) => i === idx ? { ...r, notes: val } : r));
  };

  return (
    <div className="card p-6">
      <h3 className="font-semibold mb-3">Patients</h3>
      <div className="overflow-auto">
        <table className="min-w-full text-sm" role="table" aria-label="Patient risk table">
          <thead>
            <tr>
              <th className="text-left px-2 py-2"><button onClick={() => toggleSort("name")}>Name</button></th>
              <th className="text-left px-2 py-2"><button onClick={() => toggleSort("risk")}>Risk</button></th>
              <th className="text-left px-2 py-2">Notes</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((p, idx) => (
              <tr key={idx} className="border-t">
                <td className="px-2 py-2">{p.name}</td>
                <td className="px-2 py-2">{p.risk.toFixed(2)}</td>
                <td className="px-2 py-2">
                  {editable ? (
                    <input aria-label={`Notes for ${p.name}`} className="input" value={p.notes ?? ""} onChange={(e) => updateNotes(idx, e.target.value)} />
                  ) : (
                    <span>{p.notes ?? ""}</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}


