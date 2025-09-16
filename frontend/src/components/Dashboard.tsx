"use client";
import { useAuth } from "@/context/AuthContext";
import { mockRegion, mockRisk, mockTemps, mockRiskTrend7Days, mockPatients, mockAlerts, mockReportCsv, delhiCoords } from "@/data/mockData";
import RiskScore from "@/components/RiskScore";
import TrendCharts from "@/components/TrendCharts";
import PatientTable from "@/components/PatientTable";
import ResourceSuggestions from "@/components/ResourceSuggestions";
import AlertsList from "@/components/AlertsList";
import ReportDownload from "@/components/ReportDownload";
import RiskMap from "@/components/RiskMap";
import ThemeToggle from "@/components/ThemeToggle";
import Sidebar from "@/components/Sidebar";
import ErrorBanner from "@/components/ErrorBanner";
import axios from "axios";
import { useMemo, useState } from "react";

export default function Dashboard() {
  const { role, username, logout } = useAuth();
  const labels = mockTemps.map((t) => t.label);
  const temps = mockTemps.map((t) => t.value);
  const [section, setSection] = useState("overview");
  const isAdmin = role === "Admin";
  const isClinician = role === "Clinician";
  const isAnalyst = role === "Analyst";
  const editablePatients = useMemo(() => isAdmin, [isAdmin]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function fetchPredict() {
    try {
      setLoading(true);
      setError(null);
      // const res = await axios.post("/predict", { region: mockRegion });
      // console.log(res.data);
    } catch (e: any) {
      setError("Failed to fetch prediction (mock)");
    } finally {
      setLoading(false);
    }
  }

  async function fetchReport() {
    try {
      setLoading(true);
      setError(null);
      // const res = await axios.get("/reports", { responseType: "blob" });
      // console.log(res.data);
    } catch (e: any) {
      setError("Failed to fetch report (mock)");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-800">Climate-Resilient Healthcare Dashboard</h1>
          <p className="text-xs text-gray-500">Region: {mockRegion}</p>
        </div>
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <span className="text-sm rounded-md px-2 py-1 bg-black/5">{role}</span>
          <button className="btn-primary" onClick={logout} aria-label="Logout">Logout {username ? `(${username})` : ""}</button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 pb-2">
        {error && <ErrorBanner message={error} onClose={() => setError(null)} />}
        {loading && <div className="text-sm text-gray-600 py-2">Loading...</div>}
      </div>

      <div className="max-w-6xl mx-auto px-4 pb-10 grid md:grid-cols-[16rem_1fr] gap-6">
        <Sidebar selected={section} onSelect={setSection} />
        <div className="space-y-6">
          {section === "overview" && (
            <>
              <RiskScore risk={mockRisk} />
              <TrendCharts labels={labels} temps={temps} risk7={mockRiskTrend7Days} />
              <div className="flex gap-3">
                <button className="btn-primary" onClick={fetchPredict}>Mock Predict</button>
                <button className="px-4 py-2 rounded-md border" onClick={fetchReport}>Mock Report</button>
              </div>
              <RiskMap coords={delhiCoords} risk={mockRisk} region={mockRegion} />
            </>
          )}
          {section === "patients" && (
            <PatientTable patients={mockPatients} editable={editablePatients} />
          )}
          {section === "resources" && isAdmin && (
            <ResourceSuggestions risk={mockRisk} />
          )}
          {section === "alerts" && (
            <AlertsList alerts={mockAlerts} />
          )}
          {section === "reports" && (
            <ReportDownload csv={mockReportCsv} />
          )}
          {section === "settings" && isAdmin && (
            <div className="card p-6 text-sm text-gray-600">Mock settings/profile will go here.</div>
          )}
        </div>
      </div>
    </div>
  );
}


