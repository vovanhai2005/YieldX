import { create } from 'zustand';
import { goldApi, bankApi, forexApi, cryptoApi } from '../lib/api';

const useMarketStore = create((set, get) => ({
  // ─── Gold ────────────────────────────
  gold: { data: [], count: 0, loading: false, error: null, lastUpdated: null },
  goldBrands: [],

  fetchGold: async (brand = null) => {
    set(s => ({ gold: { ...s.gold, loading: true, error: null } }));
    try {
      const res = await goldApi.getLatest(brand);
      set({ gold: { data: res.data.data, count: res.data.count, loading: false, error: null, lastUpdated: new Date() } });
    } catch (err) {
      set(s => ({ gold: { ...s.gold, loading: false, error: err.message } }));
    }
  },

  fetchGoldBrands: async () => {
    try {
      const res = await goldApi.getBrands();
      set({ goldBrands: res.data.brands });
    } catch {}
  },

  // ─── Bank Rates ──────────────────────
  bankRates: { data: [], count: 0, loading: false, error: null, lastUpdated: null },
  bankList: [],
  bankCompare: { data: [], count: 0, loading: false, error: null },

  fetchBankRates: async (params = {}) => {
    set(s => ({ bankRates: { ...s.bankRates, loading: true, error: null } }));
    try {
      const res = await bankApi.getLatest(params);
      set({ bankRates: { data: res.data.data, count: res.data.count, loading: false, error: null, lastUpdated: new Date() } });
    } catch (err) {
      set(s => ({ bankRates: { ...s.bankRates, loading: false, error: err.message } }));
    }
  },

  fetchBankList: async () => {
    try {
      const res = await bankApi.getBanks();
      set({ bankList: res.data.banks });
    } catch {}
  },

  fetchBankCompare: async (termMonths, currency = 'VND') => {
    set(s => ({ bankCompare: { ...s.bankCompare, loading: true, error: null } }));
    try {
      const res = await bankApi.compare(termMonths, currency);
      set({ bankCompare: { data: res.data.data, count: res.data.count, loading: false, error: null } });
    } catch (err) {
      set(s => ({ bankCompare: { ...s.bankCompare, loading: false, error: err.message } }));
    }
  },

  // ─── Forex ───────────────────────────
  forex: { data: [], count: 0, loading: false, error: null, lastUpdated: null },
  currencies: [],

  fetchForex: async (params = {}) => {
    set(s => ({ forex: { ...s.forex, loading: true, error: null } }));
    try {
      const res = await forexApi.getLatest(params);
      set({ forex: { data: res.data.data, count: res.data.count, loading: false, error: null, lastUpdated: new Date() } });
    } catch (err) {
      set(s => ({ forex: { ...s.forex, loading: false, error: err.message } }));
    }
  },

  fetchCurrencies: async () => {
    try {
      const res = await forexApi.getCurrencies();
      set({ currencies: res.data.currencies });
    } catch {}
  },

  // ─── Crypto ──────────────────────────
  crypto: { data: [], count: 0, loading: false, error: null, lastUpdated: null },

  fetchCrypto: async (symbol = null) => {
    set(s => ({ crypto: { ...s.crypto, loading: true, error: null } }));
    try {
      const res = await cryptoApi.getLatest(symbol);
      set({ crypto: { data: res.data.data, count: res.data.count, loading: false, error: null, lastUpdated: new Date() } });
    } catch (err) {
      set(s => ({ crypto: { ...s.crypto, loading: false, error: err.message } }));
    }
  },

  // ─── Global refresh ──────────────────
  refreshAll: async () => {
    const { fetchGold, fetchBankRates, fetchForex, fetchCrypto } = get();
    await Promise.allSettled([
      fetchGold(),
      fetchBankRates({ currency: 'VND' }),
      fetchForex(),
      fetchCrypto(),
    ]);
  },
}));

export default useMarketStore;
