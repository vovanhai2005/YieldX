import { useEffect, useState } from 'react';
import useMarketStore from '../stores/marketStore';
import Navbar from '../components/Navbar';
import DataTable from '../components/DataTable';
import LoadingSpinner from '../components/LoadingSpinner';

const fmtUSD = (n, d = 2) =>
  n != null ? `$${Number(n).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d })}` : '—';
const fmtLarge = (n) => {
  if (n == null) return '—';
  const v = Number(n);
  if (v >= 1e12) return `$${(v / 1e12).toFixed(2)}T`;
  if (v >= 1e9) return `$${(v / 1e9).toFixed(2)}B`;
  if (v >= 1e6) return `$${(v / 1e6).toFixed(2)}M`;
  return `$${v.toLocaleString('en-US')}`;
};
const fmtDate = (d) => d ? new Date(d).toLocaleString('vi-VN') : '—';

const CRYPTO_ICONS = {
  BTC: '₿', ETH: 'Ξ', BNB: '⬡', SOL: '◎', ADA: '₳',
  XRP: '✕', DOGE: 'Ð', AVAX: 'Δ', DOT: '●', MATIC: '⬡',
};

const CryptoPage = () => {
  const { crypto, fetchCrypto } = useMarketStore();
  const [symbolFilter, setSymbolFilter] = useState('');

  useEffect(() => {
    fetchCrypto();
  }, []);

  const handleSearch = (e) => {
    setSymbolFilter(e.target.value.toUpperCase());
  };

  const filtered = symbolFilter
    ? crypto.data.filter(c =>
        c.symbol?.toUpperCase().includes(symbolFilter) ||
        c.name?.toUpperCase().includes(symbolFilter)
      )
    : crypto.data;

  // Top coins for header cards
  const topCoins = ['BTC', 'ETH', 'BNB', 'SOL'];
  const topData = topCoins.map(s => crypto.data.find(c => c.symbol === s)).filter(Boolean);

  const columns = [
    {
      key: 'rank', label: '#', align: 'center',
      render: (v) => <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>{v ?? '—'}</span>,
    },
    {
      key: 'symbol', label: 'Asset',
      render: (v, row) => (
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
            style={{ background: 'rgba(59,130,246,0.1)', color: '#2563eb' }}
          >
            {CRYPTO_ICONS[v] || v?.[0]}
          </div>
          <div>
            <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>{v}</p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{row.name}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'price_usd', label: 'Price (USD)', align: 'right',
      render: (v) => (
        <span className="font-bold font-mono text-lg" style={{ color: 'var(--text-primary)' }}>
          {fmtUSD(v, Number(v) > 100 ? 2 : 4)}
        </span>
      ),
    },
    {
      key: 'price_vnd', label: 'Price (VND)', align: 'right',
      render: (v) => (
        <span className="font-mono text-sm" style={{ color: 'var(--text-secondary)' }}>
          {v != null ? `${Number(v).toLocaleString('vi-VN')} ₫` : '—'}
        </span>
      ),
    },
    {
      key: 'market_cap_usd', label: 'Market Cap', align: 'right',
      render: (v) => <span className="font-mono">{fmtLarge(v)}</span>,
    },
    {
      key: 'volume_24h_usd', label: '24h Volume', align: 'right',
      render: (v) => <span className="font-mono text-sm" style={{ color: 'var(--text-secondary)' }}>{fmtLarge(v)}</span>,
    },
    { key: 'source', label: 'Source', sortable: false },
    {
      key: 'scraped_at', label: 'Updated', sortable: false,
      render: (v) => <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{fmtDate(v)}</span>,
    },
  ];

  return (
    <div className="flex-1 overflow-auto bg-grid">
      <Navbar title="Cryptocurrency" subtitle="Live crypto prices by market cap" />

      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center gap-3">
          <span className="text-2xl">₿</span>
          <div>
            <h2 className="font-bold gradient-text-blue">Crypto Market</h2>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
              {crypto.count} assets tracked
              {crypto.lastUpdated && ` · Updated ${crypto.lastUpdated.toLocaleTimeString('vi-VN')}`}
            </p>
          </div>
        </div>

        {/* Top coin cards */}
        {!crypto.loading && topData.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 stagger-children">
            {topData.map(c => (
              <div key={c.symbol} className="glass-card p-4">
                <div className="flex items-center gap-2 mb-2">
                  <div
                    className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
                    style={{ background: 'rgba(59,130,246,0.1)', color: '#2563eb' }}
                  >
                    {CRYPTO_ICONS[c.symbol] || c.symbol?.[0]}
                  </div>
                  <div>
                    <p className="font-bold text-xs" style={{ color: 'var(--text-primary)' }}>{c.symbol}</p>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{c.name}</p>
                  </div>
                </div>
                <p className="text-xl font-bold font-mono" style={{ color: 'var(--text-primary)' }}>
                  {fmtUSD(c.price_usd, Number(c.price_usd) > 100 ? 0 : 2)}
                </p>
                <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                  Cap: {fmtLarge(c.market_cap_usd)}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Search */}
        <div className="glass-card p-4">
          <div className="flex items-center gap-3">
            <span className="text-base" style={{ color: 'var(--text-muted)' }}>🔍</span>
            <input
              id="crypto-search"
              type="text"
              placeholder="Search by symbol or name (e.g. BTC, Bitcoin)..."
              value={symbolFilter}
              onChange={handleSearch}
              className="input-glass flex-1"
            />
            {symbolFilter && (
              <button className="btn-ghost text-xs" onClick={() => setSymbolFilter('')}>✕</button>
            )}
          </div>
        </div>

        {/* Table */}
        <div className="glass-card overflow-hidden">
          <div className="px-5 py-4 border-b flex items-center justify-between" style={{ borderColor: 'var(--border-subtle)' }}>
            <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
              {symbolFilter ? `Search: "${symbolFilter}"` : 'All Cryptocurrencies'}
            </h3>
            <div className="flex items-center gap-2">
              <span className="badge-neutral text-xs">{filtered.length} assets</span>
              {crypto.error && <span className="badge-down text-xs">⚠ {crypto.error}</span>}
            </div>
          </div>
          {crypto.loading ? <LoadingSpinner /> : (
            <DataTable
              id="crypto-table"
              columns={columns}
              data={filtered}
              emptyMessage="No crypto data available."
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default CryptoPage;
