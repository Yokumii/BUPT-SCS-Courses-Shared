import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      sessionStorage.clear();
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth
export const register = (username: string, password: string, phone?: string) =>
  api.post('/auth/register', { username, password, phone });

export const login = (username: string, password: string) =>
  api.post('/auth/login', { username, password });

export const getMe = () => api.get('/auth/me');

export const recharge = (amount: number) =>
  api.post('/auth/recharge', { amount });

export const updateVehicle = (vehicleId: string, batteryCapacity: number) =>
  api.put('/auth/vehicle', { vehicle_id: vehicleId, battery_capacity: batteryCapacity });

// Charging
export const submitChargingRequest = (mode: string, kwh: number) =>
  api.post('/charging/submit', { mode, kwh });

export const modifyMode = (newMode: string) =>
  api.put('/charging/modify-mode', { new_mode: newMode });

export const modifyAmount = (newKwh: number) =>
  api.put('/charging/modify-amount', { new_kwh: newKwh });

export const cancelCharging = () => api.post('/charging/cancel');

export const viewQueueNumber = () => api.get('/charging/queue-number');

export const viewWaitingCount = () => api.get('/charging/waiting-count');

export const advanceDemoTime = (minutes: number) =>
  api.post('/charging/demo/advance-time', null, { params: { minutes } });

// Pile
export const endCharging = () => api.post('/pile/end-charging');

export const togglePile = (pileId: number, action: string) =>
  api.post('/pile/toggle', { pile_id: pileId, action });

export const viewAllPileStatus = () => api.get('/pile/status');

export const viewQueuingVehicles = (pileId: number) =>
  api.get(`/pile/queuing/${pileId}`);

export const setSchedulingPolicy = (mode: string) =>
  api.put('/pile/scheduling-policy', null, { params: { mode } });

export const reportFault = (pileId: number, strategy: string) =>
  api.post(`/pile/fault/${pileId}`, null, { params: { strategy } });

export const reportRecovery = (pileId: number) =>
  api.post(`/pile/recover/${pileId}`);

// Billing
export const viewBills = () => api.get('/billing/bills');

export const viewReport = (timeWindow: string, pileId?: number) =>
  api.get('/billing/report', { params: { time_window: timeWindow, pile_id: pileId } });

export default api;
