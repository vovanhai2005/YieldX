import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './page/Dashboard';
import GoldPage from './page/GoldPage';
import BankRatesPage from './page/BankRatesPage';
import ForexPage from './page/ForexPage';
import CryptoPage from './page/CryptoPage';

const App = () => {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/gold" element={<GoldPage />} />
          <Route path="/bank-rates" element={<BankRatesPage />} />
          <Route path="/forex" element={<ForexPage />} />
          <Route path="/crypto" element={<CryptoPage />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
