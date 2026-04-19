const StatCard = ({ icon, label, value, sub, accent = 'blue', trend = null, onClick }) => {
  const accentColors = {
    blue: { bg: 'rgba(59,130,246,0.1)', border: 'rgba(59,130,246,0.25)', icon: '#3b82f6', glow: 'rgba(59,130,246,0.2)' },
    gold: { bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.25)', icon: '#f59e0b', glow: 'rgba(245,158,11,0.2)' },
    green: { bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.25)', icon: '#10b981', glow: 'rgba(16,185,129,0.2)' },
    purple: { bg: 'rgba(139,92,246,0.1)', border: 'rgba(139,92,246,0.25)', icon: '#8b5cf6', glow: 'rgba(139,92,246,0.2)' },
    rose: { bg: 'rgba(244,63,94,0.1)', border: 'rgba(244,63,94,0.25)', icon: '#f43f5e', glow: 'rgba(244,63,94,0.2)' },
  };

  const colors = accentColors[accent] || accentColors.blue;

  return (
    <div
      id={`stat-card-${label?.toLowerCase().replace(/\s+/g, '-')}`}
      className="glass-card p-5 cursor-pointer animate-fade-up"
      style={{ borderColor: colors.border }}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center text-lg"
          style={{ background: colors.bg, color: colors.icon, boxShadow: `0 0 20px ${colors.glow}` }}
        >
          {icon}
        </div>
        {trend !== null && (
          <span className={trend >= 0 ? 'badge-up' : 'badge-down'}>
            {trend >= 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(2)}%
          </span>
        )}
      </div>

      <p className="text-xs font-medium uppercase tracking-wider mb-1" style={{ color: 'var(--text-secondary)' }}>
        {label}
      </p>
      <p className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>
        {value}
      </p>
      {sub && (
        <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
          {sub}
        </p>
      )}
    </div>
  );
};

export default StatCard;
