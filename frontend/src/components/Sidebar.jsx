import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/', icon: '⚡', label: 'Dashboard', id: 'nav-dashboard' },
  { to: '/gold', icon: '🥇', label: 'Gold Prices', id: 'nav-gold' },
  { to: '/bank-rates', icon: '🏦', label: 'Bank Rates', id: 'nav-bank-rates' },
  { to: '/forex', icon: '💱', label: 'Forex', id: 'nav-forex' },
  { to: '/crypto', icon: '₿', label: 'Crypto', id: 'nav-crypto' },
];

const Sidebar = () => {
  return (
    <aside
      className="sidebar-width h-screen flex flex-col sticky top-0"
      style={{
        background: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border-subtle)',
        backdropFilter: 'blur(20px)',
      }}
    >
      {/* Logo */}
      <div className="px-6 py-6 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center font-black text-sm text-white"
            style={{
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              boxShadow: '0 4px 20px rgba(59,130,246,0.3)',
            }}
          >
            YX
          </div>
          <div>
            <p className="font-bold text-sm tracking-wide" style={{ color: 'var(--text-primary)' }}>YieldX</p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Market Tracker</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <p className="text-xs font-semibold uppercase tracking-widest px-4 mb-3" style={{ color: 'var(--text-muted)' }}>
          Markets
        </p>
        {navItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            id={item.id}
            end={item.to === '/'}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <span className="text-base leading-none">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t" style={{ borderColor: 'var(--border-subtle)' }}>
        <div className="flex items-center gap-2">
          <span className="status-dot" style={{ background: '#059669' }} />
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
            API Connected
          </span>
        </div>
        <p className="text-xs mt-1" style={{ color: 'var(--text-muted)', opacity: 0.5 }}>
          v1.0.0 · Vietnam
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
