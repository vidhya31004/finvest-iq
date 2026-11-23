
-- Insert markets
INSERT INTO markets
(market_code, market_name, default_currency)
VALUES
('IND', 'India', 'INR'),
('USA', 'United States', 'USD')
ON CONFLICT (market_code) DO NOTHING;

-- Insert data sources
INSERT INTO data_sources
(source_name, source_type)
VALUES
('Yahoo Finance', 'MARKET_DATA'),
('Manual Entry', 'MANUAL')
ON CONFLICT (source_name) DO NOTHING;

-- Insert Indian stocks
INSERT INTO instruments
(market_id, ticker, company_name, currency, exchange_code, sector)
SELECT market_id, stock.ticker, stock.company_name,
       'INR', 'NSE', stock.sector
FROM markets
CROSS JOIN (VALUES
    ('RELIANCE.NS', 'Reliance Industries', 'Energy'),
    ('TCS.NS', 'Tata Consultancy Services', 'IT'),
    ('HDFCBANK.NS', 'HDFC Bank', 'Banking')
) AS stock(ticker, company_name, sector)
WHERE markets.market_code = 'IND'
ON CONFLICT (market_id, ticker) DO NOTHING;

-- Insert US stocks
INSERT INTO instruments
(market_id, ticker, company_name, currency, exchange_code, sector)
SELECT market_id, stock.ticker, stock.company_name,
       'USD', stock.exchange_code, stock.sector
FROM markets
CROSS JOIN (VALUES
    ('AAPL', 'Apple Inc.', 'NASDAQ', 'Technology'),
    ('MSFT', 'Microsoft Corporation', 'NASDAQ', 'Technology'),
    ('NVDA', 'NVIDIA Corporation', 'NASDAQ', 'Semiconductors')
) AS stock(ticker, company_name, exchange_code, sector)
WHERE markets.market_code = 'USA'
ON CONFLICT (market_id, ticker) DO NOTHING;
