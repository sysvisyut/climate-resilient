import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests if it exists
api.interceptors.request.use((config) => {
  // Check if we're in a browser environment
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle 401 responses (unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401 && typeof window !== "undefined") {
      // Clear token and redirect to login
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const login = async (email: string, password: string) => {
  const formData = new FormData();
  formData.append("username", email);
  formData.append("password", password);

  const response = await axios.post(`${API_URL}/auth/token`, formData);
  return response.data;
};

export const register = async (userData: {
  email: string;
  password: string;
  full_name: string;
  role: string;
  hospital_name?: string;
  location_id?: number;
}) => {
  const response = await api.post("/auth/register", userData);
  return response.data;
};

// Locations endpoints
export const getLocations = async (type?: string) => {
  const response = await api.get("/data/locations", {
    params: { location_type: type },
  });
  return response.data;
};

export const getLocation = async (id: number) => {
  const response = await api.get(`/data/locations/${id}`);
  return response.data;
};

// Climate data endpoints
export const getClimateData = async (
  locationId: number,
  params: {
    start_date?: string;
    end_date?: string;
    is_projected?: boolean;
    projection_year?: number;
  } = {}
) => {
  const response = await api.get(`/data/climate/${locationId}`, { params });
  return response.data;
};

// Health data endpoints
export const getHealthData = async (
  locationId: number,
  params: {
    start_date?: string;
    end_date?: string;
    is_projected?: boolean;
    projection_year?: number;
  } = {}
) => {
  const response = await api.get(`/data/health/${locationId}`, { params });
  return response.data;
};

// Hospital data endpoints
export const getHospitalData = async (
  locationId: number,
  params: {
    start_date?: string;
    end_date?: string;
    is_projected?: boolean;
    projection_year?: number;
  } = {}
) => {
  const response = await api.get(`/data/hospital/${locationId}`, { params });
  return response.data;
};

// Summary endpoint
export const getDataSummary = async () => {
  const response = await api.get("/data/summary");
  return response.data;
};

// Alerts endpoint
export const getAlerts = async (riskThreshold = 0.7) => {
  const response = await api.get("/data/alerts", {
    params: { risk_threshold: riskThreshold },
  });
  return response.data;
};

// Prediction endpoints
export const predictRisk = async (locationId: number, date?: string) => {
  // Always use enhanced endpoint for real-time predictions
  const response = await api.get(`/enhanced/health-risks/${locationId}`, {
    params: { use_real_time: true, date_str: date },
  });
  return response.data;
};

export const forecastDiseases = async (locationId: number, days = 7) => {
  // Use natural disasters endpoint which provides better forecasting
  const response = await api.get(`/enhanced/natural-disasters/${locationId}`, {
    params: { days_ahead: days },
  });
  return response.data;
};

export const predictResources = async (locationId: number) => {
  // Always use enhanced endpoint for real-time predictions
  const response = await api.get(`/enhanced/resource-needs/${locationId}`, {
    params: { use_real_time: true },
  });
  return response.data;
};

export const getClimateProjections = async (locationId: number, year?: number) => {
  const response = await api.get(`/predictions/climate-projections/${locationId}`, {
    params: { year },
  });
  return response.data;
};

// Enhanced prediction endpoints
export const getEnhancedHealthRisks = async (
  locationId: number,
  useRealTime = true,
  date?: string
) => {
  const response = await api.get(`/enhanced/health-risks/${locationId}`, {
    params: { use_real_time: true, date_str: date }, // Always use real-time data
  });
  return response.data;
};

export const getEnhancedResourceNeeds = async (locationId: number, useRealTime = true) => {
  const response = await api.get(`/enhanced/resource-needs/${locationId}`, {
    params: { use_real_time: true }, // Always use real-time data
  });
  return response.data;
};

export const getNaturalDisasters = async (locationId: number, daysAhead = 7) => {
  const response = await api.get(`/enhanced/natural-disasters/${locationId}`, {
    params: { days_ahead: daysAhead },
  });
  return response.data;
};

export const getPeakTimes = async (locationId: number) => {
  const response = await api.get(`/enhanced/peak-times/${locationId}`);
  return response.data;
};

export const getRealTimeWeather = async (locationId: number, updateDb = false) => {
  const response = await api.get(`/data/real-time-weather/${locationId}`, {
    params: { update_db: updateDb },
  });
  return response.data;
};

// Admin only endpoints
export const getClimateHealthCorrelation = async () => {
  const response = await api.get("/predictions/climate-health-correlation");
  return response.data;
};

export const trainModels = async () => {
  const response = await api.post("/predictions/train-models");
  return response.data;
};

export default api;
