# FINVEST IQ

### Financial Risk & Investment Intelligence Platform

FINVEST IQ is a financial analytics platform designed to analyse portfolio performance, evaluate investment risk, and understand the volatility of Indian and US equities using historical market data.

The platform combines financial analytics, data engineering, and interactive visualisation to transform historical market data into meaningful portfolio insights.

### Key Features

- **Portfolio Performance Analysis** — Track historical portfolio value and returns.
- **Stock Volatility Analysis** — Analyse 20-day and 60-day rolling volatility.
- **Value at Risk (VaR)** — Estimate potential portfolio losses at a selected confidence level.
- **Conditional Value at Risk (CVaR)** — Measure expected losses beyond the VaR threshold.
- **Maximum Drawdown** — Evaluate historical peak-to-trough portfolio declines.
- **Correlation Analysis** — Examine relationships between asset returns.
- **Stress Testing** — Evaluate portfolio behaviour under hypothetical market scenarios.
- **Multi-market Analytics** — Analyse selected Indian and US equities with currency conversion.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript |
| Visualisation | Recharts |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Data Processing | Pandas, NumPy |
| Database Integration | SQLAlchemy |
| Version Control | Git, GitHub |

## Supported Markets

**Indian Equities**
- Reliance Industries (RELIANCE.NS)
- Tata Consultancy Services (TCS.NS)
- HDFC Bank (HDFCBANK.NS)

**US Equities**
- Apple (AAPL)
- Microsoft (MSFT)
- NVIDIA (NVDA)

USD/INR exchange-rate data supports cross-market portfolio valuation.

## Project Architecture

```text
finvest-iq/
│
├── backend/
│   └── app/
│       ├── analytics/
│       │   ├── correlation.py
│       │   ├── drawdown.py
│       │   ├── portfolio_risk.py
│       │   ├── returns.py
│       │   ├── stress_test.py
│       │   ├── var.py
│       │   └── volatility.py
│       │
│       ├── api/
│       ├── db/
│       ├── ingestion/
│       └── main.py
│
├── data/
│   ├── raw/
│   │   ├── fx/
│   │   └── prices/
│   └── samples/
│
├── database/
│   └── migrations/
│
└── finvest-iq/
    └── frontend/
        ├── public/
        └── src/
            ├── components/
            └── assets/
```

## Analytics Methodology

The platform uses historical market observations to calculate portfolio and asset-level risk metrics.

- **Daily Returns:** Calculated from historical closing prices.
- **Rolling Volatility:** Evaluated using 20-day and 60-day windows.
- **Annualised Volatility:** Uses a 252-trading-day convention.
- **Portfolio Valuation:** Converts INR-denominated holdings into USD using historical exchange rates.
- **Value at Risk:** Estimates potential portfolio losses at a specified confidence level.
- **Conditional Value at Risk:** Estimates expected losses beyond the VaR threshold.
- **Drawdown Analysis:** Measures declines from historical portfolio peaks.
- **Correlation Analysis:** Examines co-movement between asset returns.
- **Stress Testing:** Evaluates hypothetical changes in market conditions.

## Getting Started

### Prerequisites

- Python 3
- Node.js and npm
- PostgreSQL
- Git

### 1. Clone the repository

```bash
git clone https://github.com/vidhya31004/finvest-iq.git
cd finvest-iq
```

### 2. Configure PostgreSQL

Create a PostgreSQL database named `finvest_iq`.

Use `finvest-iq/.env.example` as a reference for your database configuration.

Copy the example environment file into the project root:

```bash
cp finvest-iq/.env.example .env
```

Update the `DATABASE_URL` value in `.env` with your local PostgreSQL password.

The `.env` file must remain local and must never be committed to GitHub.

**Never commit your actual `.env` file or expose database credentials.**

### 3. Set up the Python environment

```bash
python3 -m venv finvest-iq/.venv
source finvest-iq/.venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

### 4. Start the backend

From the repository root:

```bash
PYTHONPATH=backend uvicorn app.main:app --reload --port 8000
```

Backend:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### 5. Start the frontend

Open a second Terminal window:

```bash
cd finvest-iq/frontend
npm install
npm run dev
```

Frontend:

`http://localhost:5173`

x## API Documentation

The backend exposes REST API endpoints for retrieving portfolio analytics and stock-level risk metrics.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/portfolio/{portfolio_id}/performance` | Retrieve historical portfolio performance |
| GET | `/api/volatility/stocks` | Retrieve stock volatility metrics |

Interactive API documentation is available through FastAPI Swagger UI:

`http://127.0.0.1:8000/docs`

## Project Limitations

- The current implementation uses historical CSV-based market data rather than live market feeds.
- Sample portfolio holdings are illustrative and are not investment recommendations.
- Historical performance and risk metrics do not predict future returns.
- Analytics depend on the available historical observations and data quality.
- Stress-testing scenarios are hypothetical rather than forecasts.

## Future Improvements

Planned enhancements include:

- Live market-data integration
- Portfolio optimisation
- Interactive risk scenario modelling
- Enhanced asset allocation analytics
- User authentication and portfolio management
- Cloud deployment and production database configuration

## Disclaimer

FINVEST IQ is an educational and analytical project intended for financial data exploration and risk analysis. It should not be considered financial or investment advice.

---

**Developed by Vidhya Shree Mohana Navaneethan**

[GitHub Repository](https://github.com/vidhya31004/finvest-iq)

