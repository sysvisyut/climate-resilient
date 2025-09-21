import { jwtDecode } from 'jwt-decode';

export interface User {
  user_id: number;
  email: string;
  full_name: string;
  role: string;
  hospital_name?: string;
  location_id?: number;
}

// Helper to safely access browser-only APIs
const isBrowser = (): boolean => typeof window !== 'undefined';

export const setAuthToken = (token: string, user: User): void => {
  if (isBrowser()) {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
  }
};

export const getAuthToken = (): string | null => {
  return isBrowser() ? localStorage.getItem('token') : null;
};

export const getUser = (): User | null => {
  if (!isBrowser()) return null;
  
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  
  try {
    return JSON.parse(userStr) as User;
  } catch (e) {
    return null;
  }
};

export const isAuthenticated = (): boolean => {
  const token = getAuthToken();
  if (!token) return false;
  
  try {
    const decoded: any = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    
    // Check if token is expired
    return decoded.exp > currentTime;
  } catch (e) {
    return false;
  }
};

export const isAdmin = (): boolean => {
  const user = getUser();
  return !!user && user.role === 'admin';
};

export const isHospitalUser = (): boolean => {
  const user = getUser();
  return !!user && user.role === 'hospital';
};

export const logout = (): void => {
  if (isBrowser()) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};

export const getUserLocationId = (): number | undefined => {
  const user = getUser();
  return user?.location_id;
};
