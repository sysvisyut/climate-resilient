import type { UserRole } from "@/context/AuthContext";

type MockUser = {
  username: string;
  password: string;
  role: UserRole;
};

export const mockUsers: MockUser[] = [
  { username: "admin", password: "admin123", role: "Admin" },
  { username: "clinician", password: "clin123", role: "Clinician" },
  { username: "analyst", password: "anal123", role: "Analyst" },
];


