
CREATE TABLE daily_prices (
    price_id BIGSERIAL PRIMARY KEY,
    instrument_id BIGINT NOT NULL REFERENCES instruments(instrument_id),
    price_date DATE NOT NULL,
    open_price NUMERIC(18,6),
    high_price NUMERIC(18,6),
    low_price NUMERIC(18,6),
    close_price NUMERIC(18,6) NOT NULL,
    adjusted_close NUMERIC(18,6),
    volume BIGINT,
    source_id BIGINT REFERENCES data_sources(source_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (instrument_id, price_date)
);

CREATE TABLE fx_rates (
    fx_id BIGSERIAL PRIMARY KEY,
    base_currency CHAR(3) NOT NULL,
    quote_currency CHAR(3) NOT NULL,
    rate_date DATE NOT NULL,
    exchange_rate NUMERIC(18,8) NOT NULL,
    source_id BIGINT REFERENCES data_sources(source_id),
    UNIQUE (base_currency, quote_currency, rate_date)
);

CREATE TABLE portfolios (
    portfolio_id BIGSERIAL PRIMARY KEY,
    portfolio_name VARCHAR(150) NOT NULL,
    base_currency CHAR(3) DEFAULT 'INR',
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
