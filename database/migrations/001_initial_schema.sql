-- FINVEST IQ: Initial database schema
-- Creates foundational market, data source, and instrument tables.

CREATE TABLE markets (
    market_id SMALLSERIAL PRIMARY KEY,
    market_code VARCHAR(10) NOT NULL UNIQUE,
    market_name VARCHAR(80) NOT NULL,
    default_currency CHAR(3) NOT NULL
);

CREATE TABLE data_sources (
    source_id BIGSERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL UNIQUE,
    source_type VARCHAR(30) NOT NULL,
    terms_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE instruments (
    instrument_id BIGSERIAL PRIMARY KEY,
    market_id SMALLINT REFERENCES markets(market_id),
    ticker VARCHAR(40) NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    instrument_type VARCHAR(30) DEFAULT 'EQUITY',
    currency CHAR(3) NOT NULL,
    exchange_code VARCHAR(30),
    sector VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (market_id, ticker)
);
