type Props = { csv: string };

export default function ReportDownload({ csv }: Props) {
  const download = () => {
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "report.csv";
    a.click();
    URL.revokeObjectURL(url);
  };
  return (
    <div className="card p-6">
      <h3 className="font-semibold mb-2">Reports</h3>
      <button className="btn-primary" onClick={download} aria-label="Download report as CSV">Download CSV</button>
    </div>
  );
}


