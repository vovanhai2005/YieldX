import { useEffect, useState } from 'react';
import useMarketStore from '../stores/marketStore';
import Navbar from '../components/Navbar';
import DataTable from '../components/DataTable';
import LoadingSpinner from '../components/LoadingSpinner';

const fmtPct = (v) => v != null ? `${Number(v).toFixed(2)}%` : '—';
const fmtDate = (d) => d ? new Date(d).toLocaleString('vi-VN') : '—';

const TERMS = [1, 3, 6, 9, 12, 18, 24, 36];

const RateBar = ({ value, max }) => {
  const pct = max > 0 ? (value / max) * 100 : 0;
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 rounded-full" style={{ background: 'rgba(0,0,0,0.06)' }}>
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${pct}%`,
            background: 'linear-gradient(90deg, #10b981, #34d399)',
          }}
        />
      </div>
      <span className="text-xs font-mono w-12 text-right" style={{ color: '#059669' }}>
        {fmtPct(value)}
      </span>
    </div>
  );
};

const BankRatesPage = () => {
  const {
    bankRates, bankList, bankCompare,
    fetchBankRates, fetchBankList, fetchBankCompare,
  } = useMarketStore();

  const [selectedBank, setSelectedBank] = useState('');
  const [selectedTerm, setSelectedTerm] = useState('');
  const [currency, setCurrency] = useState('VND');
  const [compareMode, setCompareMode] = useState(false);
  const [compareTerm, setCompareTerm] = useState(12);

  useEffect(() => {
    fetchBankList();
    fetchBankRates({ currency });
  }, []);

  const handleFilter = () => {
    const params = { currency };
    if (selectedBank) params.bank_code = selectedBank;
    if (selectedTerm) params.term_months = selectedTerm;
    fetchBankRates(params);
  };

  const handleCompare = () => {
    fetchBankCompare(compareTerm, currency);
  };

  // For coloring bar
  const maxRate = Math.max(...(compareMode ? bankCompare.data : bankRates.data).map(d => Number(d.interest_rate) || 0));

  const columns = [
    {
      key: 'bank_name', label: 'Bank',
      render: (v, row) => (
        <div>
          <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{v || row.bank_code}</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{row.bank_code}</p>
        </div>
      ),
    },
    {
      key: 'term_months', label: 'Term', align: 'center',
      render: (v) => (
        <span className="badge-neutral">{v} tháng</span>
      ),
    },
    {
      key: 'interest_rate', label: 'Interest Rate', align: 'right',
      render: (v) => (
        <span className="font-bold font-mono text-emerald-600">{fmtPct(v)}</span>
      ),
    },
    {
      key: 'interest_rate', label: 'Rate Bar', sortable: false,
      render: (v) => <RateBar value={Number(v)} max={maxRate} />,
    },
    { key: 'currency', label: 'Currency', align: 'center' },
    {
      key: 'scraped_at', label: 'Updated', sortable: false,
      render: (v) => <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{fmtDate(v)}</span>,
    },
  ];

  const activeData = compareMode ? bankCompare.data : bankRates.data;
  const isLoading = compareMode ? bankCompare.loading : bankRates.loading;

  return (
    <div className="flex-1 overflow-auto bg-grid">
      <Navbar
        title="Bank Interest Rates"
        subtitle="Deposit interest rates from Vietnamese banks"
      />

      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🏦</span>
            <div>
              <h2 className="font-bold gradient-text-green">Bank Rates</h2>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {bankRates.count} rate records
                {bankRates.lastUpdated && ` · Updated ${bankRates.lastUpdated.toLocaleTimeString('vi-VN')}`}
              </p>
            </div>
          </div>

          {/* Mode toggle */}
          <div className="flex items-center gap-2">
            <button
              id="btn-mode-browse"
              className={compareMode ? 'btn-ghost' : 'btn-primary'}
              onClick={() => setCompareMode(false)}
            >
              Browse
            </button>
            <button
              id="btn-mode-compare"
              className={compareMode ? 'btn-primary' : 'btn-ghost'}
              onClick={() => setCompareMode(true)}
            >
              Compare Banks
            </button>
          </div>
        </div>

        {/* Filters */}
        {!compareMode ? (
          <div className="glass-card p-4">
            <div className="flex flex-wrap items-end gap-3">
              <div>
                <label className="block text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>Bank</label>
                <select
                  id="bank-filter-code"
                  value={selectedBank}
                  onChange={e => setSelectedBank(e.target.value)}
                  className="input-glass"
                >
                  <option value="">All Banks</option>
                  {bankList.map(b => (
                    <option key={b.code} value={b.code}>{b.name || b.code}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>Term</label>
                <select
                  id="bank-filter-term"
                  value={selectedTerm}
                  onChange={e => setSelectedTerm(e.target.value)}
                  className="input-glass"
                >
                  <option value="">All Terms</option>
                  {TERMS.map(t => <option key={t} value={t}>{t} months</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>Currency</label>
                <select
                  id="bank-filter-currency"
                  value={currency}
                  onChange={e => setCurrency(e.target.value)}
                  className="input-glass"
                >
                  <option value="VND">VND</option>
                  <option value="USD">USD</option>
                </select>
              </div>
              <button id="btn-bank-filter" className="btn-primary" onClick={handleFilter}>
                Filter
              </button>
              <button
                className="btn-ghost"
                onClick={() => {
                  setSelectedBank(''); setSelectedTerm(''); setCurrency('VND');
                  fetchBankRates({ currency: 'VND' });
                }}
              >
                Reset
              </button>
            </div>
          </div>
        ) : (
          <div className="glass-card p-4">
            <p className="text-sm font-medium mb-3" style={{ color: 'var(--text-secondary)' }}>
              Compare all banks for a specific deposit term:
            </p>
            <div className="flex flex-wrap items-end gap-3">
              <div>
                <label className="block text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>Term (months)</label>
                <select
                  id="compare-term"
                  value={compareTerm}
                  onChange={e => setCompareTerm(Number(e.target.value))}
                  className="input-glass"
                >
                  {TERMS.map(t => <option key={t} value={t}>{t} months</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>Currency</label>
                <select
                  id="compare-currency"
                  value={currency}
                  onChange={e => setCurrency(e.target.value)}
                  className="input-glass"
                >
                  <option value="VND">VND</option>
                  <option value="USD">USD</option>
                </select>
              </div>
              <button id="btn-compare" className="btn-primary" onClick={handleCompare}>
                Compare
              </button>
            </div>
          </div>
        )}

        {/* Table */}
        <div className="glass-card overflow-hidden">
          <div className="px-5 py-4 border-b flex items-center justify-between" style={{ borderColor: 'var(--border-subtle)' }}>
            <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
              {compareMode ? `Bank Comparison — ${compareTerm}-Month Term` : 'Interest Rates'}
            </h3>
            <span className="badge-neutral text-xs">{activeData.length} records</span>
          </div>
          {isLoading ? <LoadingSpinner /> : (
            <DataTable
              id="bank-rates-table"
              columns={columns}
              data={activeData}
              emptyMessage="No rate data. Apply filters or click Compare."
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default BankRatesPage;
