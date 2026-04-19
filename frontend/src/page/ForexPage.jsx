import { useEffect, useState } from 'react';
import useMarketStore from '../stores/marketStore';
import Navbar from '../components/Navbar';
import DataTable from '../components/DataTable';
import LoadingSpinner from '../components/LoadingSpinner';

const fmtVND = (n) => n != null ? `${Number(n).toLocaleString('vi-VN')} ₫` : '—';
const fmtDate = (d) => d ? new Date(d).toLocaleString('vi-VN') : '—';

const MAJOR_PAIRS = ['USD', 'EUR', 'JPY', 'GBP', 'CNY', 'AUD', 'SGD', 'KRW'];

const ForexPage = () => {
  const { forex, currencies, fetchForex, fetchCurrencies } = useMarketStore();
  const [currencyFilter, setCurrencyFilter] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');

  useEffect(() => {
    fetchCurrencies();
    fetchForex();
  }, []);

  const handleFilter = () => {
    const params = {};
    if (currencyFilter) params.currency_code = currencyFilter;
    if (sourceFilter) params.source = sourceFilter;
    fetchForex(params);
  };

  const handleReset = () => {
    setCurrencyFilter('');
    setSourceFilter('');
    fetchForex();
  };

  // Get unique sources
  const sources = [...new Set(forex.data.map(f => f.source).filter(Boolean))];

  const columns = [
    {
      key: 'currency_code', label: 'Code',
      render: (v) => (
        <span
          className="font-bold px-2 py-0.5 rounded text-xs"
          style={{
            background: MAJOR_PAIRS.includes(v) ? 'rgba(59,130,246,0.1)' : 'rgba(0,0,0,0.04)',
            color: MAJOR_PAIRS.includes(v) ? '#2563eb' : 'var(--text-secondary)',
          }}
        >
          {v}
        </span>
      ),
    },
    { key: 'currency_name', label: 'Currency Name' },
    {
      key: 'buy_rate', label: 'Buy Rate (VND)', align: 'right',
      render: (v) => <span className="font-mono text-blue-600">{fmtVND(v)}</span>,
    },
    {
      key: 'transfer_rate', label: 'Transfer Rate (VND)', align: 'right',
      render: (v) => <span className="font-mono" style={{ color: 'var(--text-secondary)' }}>{fmtVND(v)}</span>,
    },
    {
      key: 'sell_rate', label: 'Sell Rate (VND)', align: 'right',
      render: (v) => <span className="font-mono text-emerald-600">{fmtVND(v)}</span>,
    },
    { key: 'source', label: 'Bank / Source' },
    {
      key: 'scraped_at', label: 'Updated', sortable: false,
      render: (v) => <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{fmtDate(v)}</span>,
    },
  ];

  // Major pairs summary
  const majorData = MAJOR_PAIRS.map(code => forex.data.find(f => f.currency_code === code)).filter(Boolean);

  return (
    <div className="flex-1 overflow-auto bg-grid">
      <Navbar title="Forex Exchange Rates" subtitle="Currency exchange rates from Vietnamese banks" />

      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center gap-3">
          <span className="text-2xl">💱</span>
          <div>
            <h2 className="font-bold gradient-text-blue">Forex Rates</h2>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
              {forex.count} currency pairs
              {forex.lastUpdated && ` · Updated ${forex.lastUpdated.toLocaleTimeString('vi-VN')}`}
            </p>
          </div>
        </div>

        {/* Major pairs quick cards */}
        {!forex.loading && majorData.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 stagger-children">
            {majorData.slice(0, 8).map(f => (
              <div key={f.currency_code} className="glass-card p-4">
                <div className="flex items-center justify-between mb-2">
                  <span
                    className="font-extrabold text-sm"
                    style={{ color: '#2563eb' }}
                  >
                    {f.currency_code}
                  </span>
                  <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{f.source}</span>
                </div>
                <p className="text-lg font-bold font-mono" style={{ color: 'var(--text-primary)' }}>
                  {fmtVND(f.sell_rate)}
                </p>
                <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                  Buy: {fmtVND(f.buy_rate)}
                </p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  {f.currency_name}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Filters */}
        <div className="glass-card p-4">
          <div className="flex flex-wrap items-end gap-3">
            <div>
              <label className="block text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>Currency</label>
              <select
                id="forex-currency-filter"
                value={currencyFilter}
                onChange={e => setCurrencyFilter(e.target.value)}
                className="input-glass"
              >
                <option value="">All Currencies</option>
                {currencies.map(c => (
                  <option key={c.code} value={c.code}>{c.code} — {c.name}</option>
                ))}
              </select>
            </div>
            {sources.length > 0 && (
              <div>
                <label className="block text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>Source</label>
                <select
                  id="forex-source-filter"
                  value={sourceFilter}
                  onChange={e => setSourceFilter(e.target.value)}
                  className="input-glass"
                >
                  <option value="">All Sources</option>
                  {sources.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            )}
            <button id="btn-forex-filter" className="btn-primary" onClick={handleFilter}>Filter</button>
            <button className="btn-ghost" onClick={handleReset}>Reset</button>
          </div>
        </div>

        {/* Table */}
        <div className="glass-card overflow-hidden">
          <div className="px-5 py-4 border-b flex items-center justify-between" style={{ borderColor: 'var(--border-subtle)' }}>
            <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>All Currency Pairs</h3>
            {forex.error && <span className="badge-down text-xs">⚠ {forex.error}</span>}
          </div>
          {forex.loading ? <LoadingSpinner /> : (
            <DataTable
              id="forex-table"
              columns={columns}
              data={forex.data}
              emptyMessage="No forex data available."
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default ForexPage;
