
-- Stores the stocks held in each portfolio
CREATE TABLE portfolio_holdings (
    holding_id BIGSERIAL PRIMARY KEY,
    portfolio_id BIGINT NOT NULL REFERENCES portfolios(portfolio_id),
    instrument_id BIGINT NOT NULL REFERENCES instruments(instrument_id),
    quantity NUMERIC(20,6) NOT NULL CHECK (quantity >= 0),
    average_cost NUMERIC(18,6) NOT NULL CHECK (average_cost >= 0),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (portfolio_id, instrument_id)
);

-- Stores calculated portfolio risk metrics
CREATE TABLE risk_metrics (
    risk_id BIGSERIAL PRIMARY KEY,
    portfolio_id BIGINT NOT NULL REFERENCES portfolios(portfolio_id),
    metric_date DATE NOT NULL,
    confidence_level NUMERIC(4,3) NOT NULL,
    var_1d NUMERIC(18,6),
    cvar_1d NUMERIC(18,6),
    volatility_annualized NUMERIC(18,6),
    beta NUMERIC(18,6),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (portfolio_id, metric_date, confidence_level)
);
