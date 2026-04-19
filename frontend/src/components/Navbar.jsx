import { useState, useEffect } from 'react';
import useMarketStore from '../stores/marketStore';

const Navbar = ({ title, subtitle }) => {
  const [time, setTime] = useState(new Date());
  const [refreshing, setRefreshing] = useState(false);
  const refreshAll = useMarketStore(s => s.refreshAll);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await refreshAll();
    setRefreshing(false);
  };

  const formatTime = (d) => d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const formatDate = (d) => d.toLocaleDateString('vi-VN', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });

  return (
    <header
      className="sticky top-0 z-10 flex items-center justify-between px-6 py-4"
      style={{
        background: 'var(--bg-navbar)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid var(--border-subtle)',
      }}
    >
      <div>
        <h1 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{title}</h1>
        {subtitle && <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Live clock */}
        <div className="text-right hidden sm:block">
          <p className="text-sm font-semibold font-mono" style={{ color: 'var(--text-primary)' }}>
            {formatTime(time)}
          </p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{formatDate(time)}</p>
        </div>

        {/* Refresh button */}
        <button
          id="btn-refresh-all"
          className="btn-ghost flex items-center gap-2"
          onClick={handleRefresh}
          disabled={refreshing}
        >
          <span
            className="text-sm"
            style={{ display: 'inline-block', animation: refreshing ? 'spin 0.8s linear infinite' : 'none' }}
          >
            ↻
          </span>
          <span className="text-sm hidden sm:inline">Refresh</span>
        </button>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </header>
  );
};

export default Navbar;
