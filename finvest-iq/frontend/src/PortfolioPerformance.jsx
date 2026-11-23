
import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { RefreshCw, TrendingUp } from "lucide-react";

const API_URL = "http://127.0.0.1:8000/api/portfolio/1/performance";

const ranges = [
  { label: "1M", days: 30 },
  { label: "3M", days: 90 },
  { label: "6M", days: 180 },
  { label: "1Y", days: 365 },
  { label: "ALL", days: null },
];

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;

  return (
    <div className="chart-tooltip">
      <span>{label}</span>
      <strong>{formatCurrency(payload[0].value)}</strong>
    </div>
  );
}

export default function PortfolioPerformance() {
  const [data, setData] = useState([]);
  const [range, setRange] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function fetchPerformance() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(API_URL, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`API returned ${response.status}`);
        }

        const result = await response.json();

        setData(
          result.performance.map((item) => ({
            ...item,
            date: new Date(`${item.date}T00:00:00`).toLocaleDateString(
              "en-US",
              { day: "2-digit", month: "short", year: "numeric" }
            ),
          }))
        );
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message || "Unable to load portfolio performance");
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    fetchPerformance();

    return () => controller.abort();
  }, []);

  const filteredData = (() => {
    const selectedRange = ranges.find((item) => item.label === range);

    if (!selectedRange?.days || data.length === 0) {
      return data;
    }

    return data.slice(-Math.min(selectedRange.days, data.length));
  })();

  const firstValue = filteredData[0]?.portfolio_value ?? 0;
  const latestValue = filteredData[filteredData.length - 1]?.portfolio_value ?? 0;
  const change = latestValue - firstValue;
  const changePercent = firstValue ? (change / firstValue) * 100 : 0;
  const positive = change >= 0;

  return (
    <div className="panel performance-panel">
      <div className="panel-heading">
        <div>
          <h3>Portfolio performance</h3>
          <p>Historical portfolio valuation · USD</p>
        </div>

        <div className="performance-status">
          <span />
          Live database connection
        </div>
      </div>

      {loading ? (
        <div className="chart-message">
          <RefreshCw className="loading-icon" size={22} />
          <span>Loading portfolio history...</span>
        </div>
      ) : error ? (
        <div className="chart-message chart-error">
          <span>{error}</span>
        </div>
      ) : data.length === 0 ? (
        <div className="chart-message">No portfolio history available.</div>
      ) : (
        <>
          <div className="performance-summary">
            <div>
              <span className="performance-label">Current portfolio value</span>
              <h2>{formatCurrency(latestValue)}</h2>
            </div>

            <div className={`performance-change ${positive ? "up" : "down"}`}>
              {positive ? <TrendingUp size={16} /> : <TrendingUp size={16} />}
              <strong>{positive ? "+" : ""}{changePercent.toFixed(2)}%</strong>
              <span>Selected period</span>
            </div>
          </div>

          <div className="range-selector">
            {ranges.map((item) => (
              <button
                key={item.label}
                className={range === item.label ? "selected" : ""}
                onClick={() => setRange(item.label)}
              >
                {item.label}
              </button>
            ))}
          </div>

          <div className="performance-chart">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={filteredData}
                margin={{ top: 10, right: 12, left: 5, bottom: 5 }}
              >
                <defs>
                  <linearGradient id="performanceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#879bff" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#879bff" stopOpacity={0.01} />
                  </linearGradient>
                </defs>

                <CartesianGrid
                  stroke="#29344b"
                  strokeDasharray="3 5"
                  vertical={false}
                />

                <XAxis
                  dataKey="date"
                  tick={{ fill: "#8290aa", fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  minTickGap={35}
                />

                <YAxis
                  tickFormatter={(value) => `$${(value / 1000).toFixed(1)}k`}
                  tick={{ fill: "#8290aa", fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  width={48}
                  domain={["auto", "auto"]}
                />

                <Tooltip content={<CustomTooltip />} />

                <Area
                  type="monotone"
                  dataKey="portfolio_value"
                  stroke="#91a3ff"
                  strokeWidth={2.5}
                  fill="url(#performanceGradient)"
                  activeDot={{ r: 5, fill: "#b7c2ff", stroke: "#111a2d", strokeWidth: 2 }}
                  dot={false}
                  animationDuration={800}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-footer">
            <span>{filteredData[0]?.date} — {filteredData[filteredData.length - 1]?.date}</span>
            <span>{filteredData.length} valuation observations</span>
          </div>
        </>
      )}
    </div>
  );
}
