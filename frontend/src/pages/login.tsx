import type { NextPage } from "next";
import { useRouter } from "next/router";
import { useAuth } from "@/context/AuthContext";
import { useEffect, useState } from "react";

const LoginPage: NextPage = () => {
  const router = useRouter();
  const { login, isAuthenticated } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) router.replace("/");
  }, [isAuthenticated, router]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const ok = login(username.trim(), password);
    if (!ok) {
      setError("Invalid credentials");
      return;
    }
    router.replace("/");
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-6">
      <div className="max-w-md w-full card p-8">
        <h1 className="text-2xl font-semibold text-center mb-6">Climate-Resilient Healthcare</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm mb-1">Username</label>
            <input className="input" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="admin or clinician" />
          </div>
          <div>
            <label className="block text-sm mb-1">Password</label>
            <input type="password" className="input" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="admin123 or clin123" />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button className="btn-primary w-full" type="submit">Login</button>
        </form>
        <div className="text-xs text-gray-500 mt-4">
          Demo users:
          <div>Admin: admin / admin123</div>
          <div>Clinician: clinician / clin123</div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;


