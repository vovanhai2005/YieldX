import { useEffect, useState } from 'react';
import useMarketStore from '../stores/marketStore';
import Navbar from '../components/Navbar';
import DataTable from '../components/DataTable';
import LoadingSpinner from '../components/LoadingSpinner';

const fmtVND = (n) => n != null ? `${Number(n).toLocaleString('vi-VN')} ₫` : '—';
const fmtDate = (d) => d ? new Date(d).toLocaleString('vi-VN') : '—';

const GoldPage = () => {
  const { gold, goldBrands, fetchGold, fetchGoldBrands } = useMarketStore();
  const [selectedBrand, setSelectedBrand] = useState('');

  useEffect(() => {
    fetchGoldBrands();
    fetchGold(selectedBrand || null);
  }, []);

  const handleBrandChange = (e) => {
    setSelectedBrand(e.target.value);
    fetchGold(e.target.value || null);
  };

  const columns = [
    { key: 'brand', label: 'Brand', render: (v) => (
      <span className="font-semibold" style={{ color: '#b45309' }}>{v}</span>
    )},
    { key: 'product_type', label: 'Product Type' },
    {
      key: 'buy_price', label: 'Buy Price (VND)', align: 'right',
      render: (v) => <span className="font-mono text-blue-600">{fmtVND(v)}</span>,
    },
    {
      key: 'sell_price', label: 'Sell Price (VND)', align: 'right',
      render: (v) => <span className="font-mono text-emerald-600">{fmtVND(v)}</span>,
    },
    {
      key: 'buy_price', label: 'Spread', sortable: false, align: 'right',
      render: (_, row) => {
        if (row.buy_price == null || row.sell_price == null) return '—';
        const spread = Number(row.sell_price) - Number(row.buy_price);
        return (
          <span className="font-mono" style={{ color: spread > 0 ? '#e11d48' : 'var(--text-secondary)' }}>
            {spread.toLocaleString('vi-VN')} ₫
          </span>
        );
      },
    },
    { key: 'source', label: 'Source' },
    {
      key: 'scraped_at', label: 'Updated', sortable: false,
      render: (v) => <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{fmtDate(v)}</span>,
    },
  ];

  return (
    <div className="flex-1 overflow-auto bg-grid">
      <Navbar
        title="Gold Prices"
        subtitle="Live gold buy/sell prices from Vietnamese dealers"
      />

      <div className="p-6 space-y-6">
        {/* Header row */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🥇</span>
            <div>
              <h2 className="font-bold gradient-text-gold">Gold Market</h2>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {gold.count} price records
                {gold.lastUpdated && ` · Updated ${gold.lastUpdated.toLocaleTimeString('vi-VN')}`}
              </p>
            </div>
          </div>

          {/* Brand filter */}
          <div className="flex items-center gap-2">
            <label className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
              Brand:
            </label>
            <select
              id="gold-brand-filter"
              value={selectedBrand}
              onChange={handleBrandChange}
              className="input-glass"
            >
              <option value="">All Brands</option>
              {goldBrands.map(b => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
            {selectedBrand && (
              <button
                className="btn-ghost text-xs"
                onClick={() => { setSelectedBrand(''); fetchGold(null); }}
              >
                ✕ Clear
              </button>
            )}
          </div>
        </div>

        {/* Summary cards */}
        {!gold.loading && gold.data.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 stagger-children">
            {['SJC', 'DOJI', 'PNJ', 'BTMC'].map(brand => {
              const entry = gold.data.find(g => g.brand === brand);
              if (!entry) return null;
              return (
                <div key={brand} className="glass-card p-4">
                  <p className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: '#b45309' }}>{brand}</p>
                  <p className="text-lg font-bold font-mono" style={{ color: 'var(--text-primary)' }}>
                    {fmtVND(entry.sell_price)}
                  </p>
                  <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                    Buy: {fmtVND(entry.buy_price)}
                  </p>
                </div>
              );
            })}
          </div>
        )}

        {/* Main table */}
        <div className="glass-card overflow-hidden">
          <div className="px-5 py-4 border-b flex items-center justify-between" style={{ borderColor: 'var(--border-subtle)' }}>
            <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>All Gold Prices</h3>
            {gold.error && (
              <span className="badge-down text-xs">⚠ {gold.error}</span>
            )}
          </div>
          {gold.loading ? (
            <LoadingSpinner />
          ) : (
            <DataTable
              id="gold-table"
              columns={columns}
              data={gold.data}
              emptyMessage="No gold price data. Try fetching from the backend."
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default GoldPage;
