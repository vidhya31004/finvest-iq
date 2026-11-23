
import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

const API_URL = "http://127.0.0.1:8000/api/volatility/stocks";

function formatPercent(value) {
  if (value === null || value === undefined) return "—";
  return `${(value * 100).toFixed(2)}%`;
}

export default function StockVolatility() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchVolatility() {
      try {
        const response = await fetch(API_URL);

        if (!response.ok) {
          throw new Error(`API request failed: ${response.status}`);
        }

        const data = await response.json();
        setStocks(data.stocks || []);
      } catch (err) {
        setError(err.message || "Unable to load volatility data.");
      } finally {
        setLoading(false);
      }
    }

    fetchVolatility();
  }, []);

  if (loading) {
    return <section className="volatility-section">Loading stock volatility...</section>;
  }

  if (error) {
    return (
      <section className="volatility-section">
        <p>Unable to load volatility data: {error}</p>
      </section>
    );
  }

  const chartData = stocks.map((stock) => ({
    ticker: stock.ticker,
    volatility: stock.latest_annualised_20d == null
      ? 0
      : stock.latest_annualised_20d * 100,
  }));

  return (
    <section className="volatility-section" id="volatility">
      <div className="section-heading">
        <div>
          <h2>Stock Volatility Analysis</h2>
          <p>Annualised historical volatility across your six holdings</p>
        </div>
        <span className="live-indicator">API CONNECTED</span>
      </div>

      <div className="volatility-table-wrapper">
        <table className="volatility-table">
          <thead>
            <tr>
              <th>Stock</th>
              <th>20-Day Volatility</th>
              <th>60-Day Volatility</th>
              <th>Annualised 20-Day</th>
              <th>Annualised 60-Day</th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((stock) => (
              <tr key={stock.ticker}>
                <td>{stock.ticker}</td>
                <td>{formatPercent(stock.latest_20d_volatility)}</td>
                <td>{formatPercent(stock.latest_60d_volatility)}</td>
                <td>{formatPercent(stock.latest_annualised_20d)}</td>
                <td>{formatPercent(stock.latest_annualised_60d)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="volatility-chart">
        <h3>Annualised 20-Day Volatility Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#263247" />
            <XAxis dataKey="ticker" stroke="#9CA3AF" />
            <YAxis
              stroke="#9CA3AF"
              tickFormatter={(value) => `${value.toFixed(0)}%`}
            />
            <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
            <Bar dataKey="volatility" fill="#38BDF8" radius={[5, 5, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="volatility-note">
        Methodology: Rolling standard deviation of daily returns,
        annualised using √252 trading days. Historical volatility is
        backward-looking and does not predict future returns.
      </p>
    </section>
  );
}
