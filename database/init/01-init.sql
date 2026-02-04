-- Initialize GenX-FX Trading Platform Database

CREATE DATABASE IF NOT EXISTS genxdb_fx_db;
USE genxdb_fx_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Trading accounts table
CREATE TABLE IF NOT EXISTS trading_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    account_name VARCHAR(100) NOT NULL,
    broker VARCHAR(50) NOT NULL,
    account_number VARCHAR(100),
    balance DECIMAL(15,2) DEFAULT 0.00,
    currency VARCHAR(10) DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Trading pairs table
CREATE TABLE IF NOT EXISTS trading_pairs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    base_currency VARCHAR(10) NOT NULL,
    quote_currency VARCHAR(10) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Optimization: Index on is_active column
-- This index improves the performance of queries that filter trading pairs by their active status,
-- such as the `/trading-pairs` endpoint.
CREATE INDEX idx_trading_pairs_is_active ON trading_pairs(is_active);

-- Market data table
CREATE TABLE IF NOT EXISTS market_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open_price DECIMAL(15,5),
    high_price DECIMAL(15,5),
    low_price DECIMAL(15,5),
    close_price DECIMAL(15,5),
    volume DECIMAL(20,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_timestamp (symbol, timestamp)
);

-- Trading signals table
CREATE TABLE IF NOT EXISTS trading_signals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(20) NOT NULL,
    confidence DECIMAL(5,2),
    price DECIMAL(15,5),
    timestamp TIMESTAMP NOT NULL,
    model_version VARCHAR(50),
    features JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_timestamp (symbol, timestamp)
);

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    account_id INT,
    symbol VARCHAR(20) NOT NULL,
    trade_type VARCHAR(10) NOT NULL,
    quantity DECIMAL(15,5) NOT NULL,
    price DECIMAL(15,5) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    signal_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (account_id) REFERENCES trading_accounts(id),
    FOREIGN KEY (signal_id) REFERENCES trading_signals(id)
);

-- Insert initial data
INSERT INTO users (username, email, password_hash) VALUES
('admin', 'admin@genxdbxfx1.com', 'hashed_password_placeholder')
ON DUPLICATE KEY UPDATE username=username;

INSERT INTO trading_pairs (symbol, base_currency, quote_currency) VALUES
('EUR/USD', 'EUR', 'USD'),
('GBP/USD', 'GBP', 'USD'),
('USD/JPY', 'USD', 'JPY'),
('USD/CHF', 'USD', 'CHF'),
('AUD/USD', 'AUD', 'USD'),
('USD/CAD', 'USD', 'CAD'),
('NZD/USD', 'NZD', 'USD'),
('EUR/GBP', 'EUR', 'GBP'),
('EUR/JPY', 'EUR', 'JPY'),
('GBP/JPY', 'GBP', 'JPY')
ON DUPLICATE KEY UPDATE symbol=symbol;
