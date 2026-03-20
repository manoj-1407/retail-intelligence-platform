
import axios from 'axios';

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({ baseURL: BASE });

let _token: string | null = null;

export async function login(username: string, password: string): Promise<string> {
  const res = await api.post('/auth/token', { username, password });
  _token = res.data.access_token as string;
  api.defaults.headers.common['Authorization'] = `Bearer ${_token}`;
  localStorage.setItem('rip_token', _token!);
  return _token!;
}

export function loadStoredToken() {
  const t = localStorage.getItem('rip_token');
  if (t) {
    _token = t;
    api.defaults.headers.common['Authorization'] = `Bearer ${t}`;
  }
  return t;
}

export const getProducts   = (params?: object) => api.get('/products',  { params }).then(r => r.data);
export const getShipments  = (params?: object) => api.get('/shipments', { params }).then(r => r.data);
export const getInventory  = (params?: object) => api.get('/inventory', { params }).then(r => r.data);
export const getSummary    = ()                => api.get('/analytics/summary').then(r => r.data);
