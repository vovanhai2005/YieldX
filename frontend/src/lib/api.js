import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

// Gold
export const goldApi = {
  getLatest: (brand = null) =>
    api.get('/gold/latest', { params: brand ? { brand } : {} }),
  getHistory: (params = {}) =>
    api.get('/gold/history', { params }),
  getBrands: () =>
    api.get('/gold/brands'),
};

// Bank Rates
export const bankApi = {
  getLatest: (params = {}) =>
    api.get('/bank-rates/latest', { params }),
  getHistory: (params = {}) =>
    api.get('/bank-rates/history', { params }),
  getBanks: () =>
    api.get('/bank-rates/banks'),
  compare: (term_months, currency = 'VND') =>
    api.get('/bank-rates/compare', { params: { term_months, currency } }),
};

// Forex
export const forexApi = {
  getLatest: (params = {}) =>
    api.get('/forex/latest', { params }),
  getHistory: (params = {}) =>
    api.get('/forex/history', { params }),
  getCurrencies: () =>
    api.get('/forex/currencies'),
};

// Crypto
export const cryptoApi = {
  getLatest: (symbol = null) =>
    api.get('/crypto/latest', { params: symbol ? { symbol } : {} }),
  getHistory: (params = {}) =>
    api.get('/crypto/history', { params }),
  getSymbols: () =>
    api.get('/crypto/symbols'),
};

// Health
export const healthApi = {
  check: () => api.get('/'),
};
