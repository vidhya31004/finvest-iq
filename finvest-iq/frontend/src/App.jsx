
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Bell,
  BriefcaseBusiness,
  ChevronDown,
  CircleHelp,
  LayoutDashboard,
  PieChart,
  Search,
  Settings,
  ShieldCheck,
  TrendingUp,
  Wallet,
} from "lucide-react";

import "./App.css";
import StockVolatility from "./components/StockVolatility";
import PortfolioPerformance from "./PortfolioPerformance";

const holdings = [
  { ticker: "AAPL", name: "Apple Inc.", allocation: 38.46, value: "$3,519.09", color: "#8b9cf7" },
  { ticker: "MSFT", name: "Microsoft Corporation", allocation: 27.66, value: "$2,531.17", color: "#69b8c9" },
  { ticker: "NVDA", name: "NVIDIA Corporation", allocation: 25.49, value: "$2,332.00", color: "#a78bfa" },
  { ticker: "RELIANCE", name: "Reliance Industries", allocation: 3.20, value: "$292.43", color: "#e6b566" },
  { ticker: "HDFCBANK", name: "HDFC Bank", allocation: 2.38, value: "$217.95", color: "#70bd99" },
  { ticker: "TCS", name: "Tata Consultancy Services", allocation: 2.81, value: "$257.42", color: "#d28eaa" },
];

const stressTests = [
  { name: "US Market Crash", loss: "9.16%", value: "$838.22" },
  { name: "India Market Crash", loss: "1.26%", value: "$115.18" },
  { name: "Global Market Crash", loss: "10.42%", value: "$953.40" },
  { name: "INR Depreciation", loss: "0.40%", value: "$36.56" },
  { name: "Combined Crisis", loss: "20.72%", value: "$1,895.83", severe: true },
];

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark"><Activity size={23} /></div>
        <div>
          <h2>FINVEST<span>IQ</span></h2>
          <p>INVESTMENT INTELLIGENCE</p>
        </div>
      </div>

      <div className="nav-section">
        <p className="nav-label">WORKSPACE</p>
        <a className="nav-item active" href="#dashboard"><LayoutDashboard size={18} /> Dashboard</a>
        <a className="nav-item" href="#portfolio"><BriefcaseBusiness size={18} /> Portfolio</a>
        <a className="nav-item" href="#markets"><TrendingUp size={18} /> Markets</a>
        <a className="nav-item" href="#analytics"><BarChart3 size={18} /> Analytics</a>
      </div>

      <div className="nav-section">
        <p className="nav-label">RISK MANAGEMENT</p>
        <a className="nav-item" href="#risk"><ShieldCheck size={18} /> Risk overview</a>
        <a className="nav-item" href="#stress"><Activity size={18} /> Stress testing</a>
        <a className="nav-item" href="#allocation"><PieChart size={18} /> Asset allocation</a>
        <a className="nav-item" href="#volatility"><TrendingUp size={18} /> Stock volatility</a>
      </div>

      <div className="sidebar-bottom">
        <a className="nav-item" href="#help"><CircleHelp size={18} /> Help & support</a>
        <a className="nav-item" href="#settings"><Settings size={18} /> Settings</a>
        <div className="profile">
          <div className="avatar">V</div>
          <div className="profile-info">
            <strong>Portfolio Manager</strong>
            <span>Personal workspace</span>
          </div>
          <ChevronDown size={16} />
        </div>
      </div>
    </aside>
  );
}

function MetricCard({ label, value, change, icon: Icon, tone = "blue", note }) {
  return (
    <div className="metric-card">
      <div className="metric-top">
        <span>{label}</span>
        <div className={`metric-icon ${tone}`}><Icon size={18} /></div>
      </div>
      <h2>{value}</h2>
      <div className="metric-bottom">
        {change && <span className="metric-change">{change}</span>}
        <span>{note}</span>
      </div>
    </div>
  );
}

function Allocation() {
  return (
    <div className="panel" id="allocation">
      <div className="panel-heading">
        <div>
          <h3>Portfolio allocation</h3>
          <p>Distribution by holding · USD</p>
        </div>
        <button className="subtle-button">View details <ArrowUpRight size={14} /></button>
      </div>

      <div className="allocation-bar">
        {holdings.map((item) => (
          <div
            key={item.ticker}
            style={{ width: `${item.allocation}%`, background: item.color }}
            title={`${item.ticker}: ${item.allocation}%`}
          />
        ))}
      </div>

      <div className="holding-list">
        {holdings.map((item) => (
          <div className="holding-row" key={item.ticker}>
            <div className="holding-name">
              <span className="legend-dot" style={{ background: item.color }} />
              <div>
                <strong>{item.ticker}</strong>
                <span>{item.name}</span>
              </div>
            </div>
            <strong>{item.allocation.toFixed(2)}%</strong>
            <span className="holding-value">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function StressTesting() {
  return (
    <div className="panel" id="stress">
      <div className="panel-heading">
        <div>
          <h3>Stress test scenarios</h3>
          <p>Hypothetical portfolio impact</p>
        </div>
        <span className="scenario-tag">5 scenarios</span>
      </div>

      <div className="stress-list">
        {stressTests.map((scenario) => (
          <div className="stress-row" key={scenario.name}>
            <div>
              <strong>{scenario.name}</strong>
              <span>Estimated portfolio loss</span>
            </div>
            <div className="stress-result">
              <strong className={scenario.severe ? "severe" : ""}>−{scenario.loss}</strong>
              <span>−{scenario.value}</span>
            </div>
          </div>
        ))}
      </div>
      <p className="panel-footnote">Static shock scenarios; not forecasts or probability estimates.</p>
    </div>
  );
}

function App() {
  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> Risk dashboard</div>
          <div className="topbar-actions">
            <div className="data-status"><span /> Historical data snapshot</div>
            <button className="icon-button" aria-label="Search"><Search size={18} /></button>
            <button className="icon-button notification" aria-label="Notifications"><Bell size={18} /></button>
            <div className="top-avatar">V</div>
          </div>
        </header>

        <div className="dashboard-content">
          <section className="welcome-row" id="dashboard">
            <div>
              <p className="eyebrow">THURSDAY, 19 NOVEMBER 2026</p>
              <h1>Risk dashboard</h1>
              <p className="page-subtitle">A clear view of your portfolio performance and risk exposure.</p>
            </div>
            <button className="date-button">
              <Wallet size={16} /> Test portfolio <ChevronDown size={15} />
            </button>
          </section>

          <section className="market-strip" id="markets">
            <div className="market-strip-title">MARKET COVERAGE</div>
            <div className="market-chip">
              <span className="market-flag">IN</span>
              <div><strong>INDIA</strong><span>INR · NSE</span></div>
              <span className="market-live">TRACKED</span>
            </div>
            <div className="market-chip">
              <span className="market-flag us">US</span>
              <div><strong>UNITED STATES</strong><span>USD · NASDAQ / NYSE</span></div>
              <span className="market-live">TRACKED</span>
            </div>
            <div className="market-updated">Prices through 17 Nov 2026</div>
          </section>

          <section className="metrics-grid" id="risk">
            <MetricCard label="Portfolio value" value="$9,150.06" change="6 holdings" icon={Wallet} tone="blue" note="Latest common valuation date" />
            <MetricCard label="Annualised volatility" value="20.93%" change="Portfolio risk" icon={Activity} tone="purple" note="Based on historical returns" />
            <MetricCard label="Value at Risk · 95%" value="1.80%" change="1-day historical VaR" icon={ShieldCheck} tone="orange" note="Historical simulation" />
            <MetricCard label="Conditional VaR · 95%" value="2.94%" change="Expected tail loss" icon={ArrowDownRight} tone="red" note="Average loss beyond VaR" />
          </section>

          <section className="content-grid" id="portfolio">
            <Allocation />
            <StressTesting />
            <PortfolioPerformance />
          </section>

          {/* New live stock volatility section */}
          <StockVolatility />

          <section className="bottom-grid" id="analytics">
            <div className="panel insight-panel">
              <div className="panel-heading">
                <div><h3>Risk snapshot</h3><p>Key portfolio observations</p></div>
                <ShieldCheck size={19} className="muted-icon" />
              </div>
              <div className="insight-item">
                <div className="insight-icon purple"><PieChart size={17} /></div>
                <div><strong>US equity concentration</strong><p>91.61% of portfolio value is allocated to US-listed holdings.</p></div>
              </div>
              <div className="insight-item">
                <div className="insight-icon orange"><Activity size={17} /></div>
                <div><strong>Combined crisis scenario</strong><p>A hypothetical combined shock produces a 20.72% portfolio loss.</p></div>
              </div>
              <div className="insight-item">
                <div className="insight-icon green"><TrendingUp size={17} /></div>
                <div><strong>Cross-market exposure</strong><p>Your portfolio includes both USD and INR-denominated assets.</p></div>
              </div>
            </div>

            <div className="panel methodology-panel">
              <div className="panel-heading">
                <div><h3>Data & methodology</h3><p>About this dashboard</p></div>
                <BarChart3 size={19} className="muted-icon" />
              </div>
              <div className="method-row"><span>Price observations</span><strong>1,494</strong></div>
              <div className="method-row"><span>FX observations</span><strong>256</strong></div>
              <div className="method-row"><span>Portfolio return observations</span><strong>237</strong></div>
              <div className="method-row"><span>Valuation date</span><strong>17 Nov 2026</strong></div>
              <p className="panel-footnote">Historical calculations use the current imported CSV data. Figures exclude taxes, transaction costs and dividends.</p>
            </div>
          </section>

          <footer className="dashboard-footer">
            <span>FINVEST IQ · INVESTMENT INTELLIGENCE</span>
            <span>Historical analytics · Not investment advice</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;
