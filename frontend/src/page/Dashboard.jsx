import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useMarketStore from '../stores/marketStore';
import Navbar from '../components/Navbar';
import StatCard from '../components/StatCard';
import LoadingSpinner from '../components/LoadingSpinner';

const fmt = (n, decimals = 2) =>
  n != null ? Number(n).toLocaleString('vi-VN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) : '—';

const fmtVND = (n) => n != null ? `${Number(n).toLocaleString('vi-VN')} ₫` : '—';

const QuickTable = ({ rows, col1, col2, col3 }) => (
  <div className="overflow-x-auto">
    <table className="data-table text-xs">
      <thead>
        <tr>
          <th>{col1}</th>
          <th>{col2}</th>
          <th>{col3}</th>
        </tr>
      </thead>
      <tbody>
        {rows.slice(0, 5).map((r, i) => (
          <tr key={i}>
            <td className="font-medium">{r.a}</td>
            <td>{r.b}</td>
            <td>{r.c}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const Dashboard = () => {
  const navigate = useNavigate();
  const {
    gold, bankRates, forex, crypto,
    fetchGold, fetchBankRates, fetchForex, fetchCrypto,
  } = useMarketStore();

  useEffect(() => {
    if (!gold.data.length) fetchGold();
    if (!bankRates.data.length) fetchBankRates({ currency: 'VND' });
    if (!forex.data.length) fetchForex();
    if (!crypto.data.length) fetchCrypto();
  }, []);

  // ── Summaries ──
  const topGold = gold.data.find(g => g.brand === 'SJC') || gold.data[0];
  const bestBankRate = [...bankRates.data].sort((a, b) => b.interest_rate - a.interest_rate)[0];
  const btc = crypto.data.find(c => c.symbol === 'BTC') || crypto.data[0];
  const usd = forex.data.find(f => f.currency_code === 'USD');

  const summaryLoading = gold.loading || bankRates.loading || forex.loading || crypto.loading;

  // ── Quick preview rows ──
  const goldRows = gold.data.slice(0, 5).map(g => ({
    a: `${g.brand} ${g.product_type}`,
    b: fmtVND(g.buy_price),
    c: fmtVND(g.sell_price),
  }));

  const bankRows = [...bankRates.data]
    .sort((a, b) => b.interest_rate - a.interest_rate)
    .slice(0, 5)
    .map(b => ({
      a: b.bank_name || b.bank_code,
      b: `${b.term_months} tháng`,
      c: `${Number(b.interest_rate).toFixed(2)}%`,
    }));

  const cryptoRows = crypto.data.slice(0, 5).map(c => ({
    a: c.symbol,
    b: `$${Number(c.price_usd).toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
    c: c.name,
  }));

  const forexRows = forex.data.slice(0, 5).map(f => ({
    a: f.currency_code,
    b: fmtVND(f.buy_rate),
    c: fmtVND(f.sell_rate),
  }));

  return (
    <div className="flex-1 overflow-auto bg-grid">
      <Navbar
        title="Market Dashboard"
        subtitle="Real-time overview of Vietnamese financial markets"
      />

      <div className="p-6 space-y-8">
        {/* Hero banner */}
        <div
          className="rounded-2xl p-6 relative overflow-hidden"
          style={{
            background: 'linear-gradient(135deg, rgba(59,130,246,0.08) 0%, rgba(139,92,246,0.06) 50%, rgba(16,185,129,0.04) 100%)',
            border: '1px solid rgba(59,130,246,0.15)',
          }}
        >
          <div className="relative z-10">
            <p className="text-xs font-semibold uppercase tracking-widest mb-2" style={{ color: '#2563eb' }}>
              ⚡ Live Market Data · Vietnam
            </p>
            <h2 className="text-3xl font-black mb-1" style={{ color: 'var(--text-primary)' }}>
              YieldX Financial Dashboard
            </h2>
            <p style={{ color: 'var(--text-secondary)' }} className="text-sm max-w-xl">
              Track gold prices, bank interest rates, forex exchange rates, and cryptocurrency data — all scraped in real time from Vietnamese sources.
            </p>
          </div>
          {/* Decorative orbs */}
          <div className="absolute top-0 right-0 w-64 h-64 rounded-full opacity-[0.06]"
            style={{ background: 'radial-gradient(circle, #3b82f6, transparent)', transform: 'translate(30%, -30%)' }} />
          <div className="absolute bottom-0 right-32 w-32 h-32 rounded-full opacity-[0.06]"
            style={{ background: 'radial-gradient(circle, #8b5cf6, transparent)', transform: 'translateY(40%)' }} />
        </div>

        {/* Stat Cards */}
        {summaryLoading ? (
          <LoadingSpinner text="Fetching market data..." />
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 stagger-children">
            <StatCard
              id="stat-gold"
              icon="🥇"
              label="SJC Gold Sell"
              value={fmtVND(topGold?.sell_price)}
              sub={topGold ? `${topGold.brand} · ${topGold.product_type}` : 'No data'}
              accent="gold"
              onClick={() => navigate('/gold')}
            />
            <StatCard
              icon="🏦"
              label="Best Bank Rate"
              value={bestBankRate ? `${Number(bestBankRate.interest_rate).toFixed(2)}%` : '—'}
              sub={bestBankRate ? `${bestBankRate.bank_name || bestBankRate.bank_code} · ${bestBankRate.term_months}mo` : 'No data'}
              accent="green"
              onClick={() => navigate('/bank-rates')}
            />
            <StatCard
              icon="₿"
              label="Bitcoin (BTC)"
              value={btc ? `$${Number(btc.price_usd).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}` : '—'}
              sub={btc ? `Rank #${btc.rank ?? 1}` : 'No data'}
              accent="purple"
              onClick={() => navigate('/crypto')}
            />
            <StatCard
              icon="💱"
              label="USD/VND Sell"
              value={usd ? fmtVND(usd.sell_rate) : '—'}
              sub={usd ? `Source: ${usd.source}` : 'No data'}
              accent="blue"
              onClick={() => navigate('/forex')}
            />
          </div>
        )}

        {/* 2x2 quick preview grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Gold preview */}
          <div className="glass-card p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-lg">🥇</span>
                <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
                  Gold Prices
                </h3>
                <span className="badge-neutral">{gold.count}</span>
              </div>
              <button className="btn-ghost text-xs" onClick={() => navigate('/gold')}>
                View all →
              </button>
            </div>
            {gold.loading ? <LoadingSpinner size="sm" text="" /> : (
              <QuickTable rows={goldRows} col1="Brand / Type" col2="Buy" col3="Sell" />
            )}
          </div>

          {/* Bank rates preview */}
          <div className="glass-card p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-lg">🏦</span>
                <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
                  Top Bank Rates
                </h3>
                <span className="badge-neutral">{bankRates.count}</span>
              </div>
              <button className="btn-ghost text-xs" onClick={() => navigate('/bank-rates')}>
                View all →
              </button>
            </div>
            {bankRates.loading ? <LoadingSpinner size="sm" text="" /> : (
              <QuickTable rows={bankRows} col1="Bank" col2="Term" col3="Rate" />
            )}
          </div>

          {/* Crypto preview */}
          <div className="glass-card p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-lg">₿</span>
                <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
                  Crypto Prices
                </h3>
                <span className="badge-neutral">{crypto.count}</span>
              </div>
              <button className="btn-ghost text-xs" onClick={() => navigate('/crypto')}>
                View all →
              </button>
            </div>
            {crypto.loading ? <LoadingSpinner size="sm" text="" /> : (
              <QuickTable rows={cryptoRows} col1="Symbol" col2="Price (USD)" col3="Name" />
            )}
          </div>

          {/* Forex preview */}
          <div className="glass-card p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-lg">💱</span>
                <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
                  Forex Rates
                </h3>
                <span className="badge-neutral">{forex.count}</span>
              </div>
              <button className="btn-ghost text-xs" onClick={() => navigate('/forex')}>
                View all →
              </button>
            </div>
            {forex.loading ? <LoadingSpinner size="sm" text="" /> : (
              <QuickTable rows={forexRows} col1="Currency" col2="Buy" col3="Sell" />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
