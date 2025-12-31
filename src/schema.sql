-- Database schema for Naked Nuras Loves Rave Music NFT Database

-- Table for storing local music files
CREATE TABLE IF NOT EXISTS music_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    file_name TEXT NOT NULL,
    file_size INTEGER,
    file_hash TEXT UNIQUE,
    mime_type TEXT,
    duration_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing music metadata
CREATE TABLE IF NOT EXISTS music_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    title TEXT,
    artist TEXT,
    album TEXT,
    genre TEXT,
    year INTEGER,
    bpm INTEGER,
    key TEXT,
    FOREIGN KEY (file_id) REFERENCES music_files(id) ON DELETE CASCADE
);

-- Table for storing NFT information
CREATE TABLE IF NOT EXISTS nft_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER,
    token_id TEXT,
    contract_address TEXT,
    chain_id TEXT DEFAULT 'avalanche',
    mint_date TIMESTAMP,
    owner_address TEXT,
    metadata_uri TEXT,
    price REAL,
    currency TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES music_files(id) ON DELETE SET NULL
);

-- Table for storing Avalanche transaction history
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nft_id INTEGER NOT NULL,
    tx_hash TEXT NOT NULL UNIQUE,
    tx_type TEXT NOT NULL,
    from_address TEXT,
    to_address TEXT,
    amount REAL,
    currency TEXT,
    block_number INTEGER,
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nft_id) REFERENCES nft_records(id) ON DELETE CASCADE
);

-- Table for storing collection information
CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    contract_address TEXT UNIQUE,
    chain_id TEXT DEFAULT 'avalanche',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Junction table for NFTs and collections
CREATE TABLE IF NOT EXISTS nft_collections (
    nft_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    PRIMARY KEY (nft_id, collection_id),
    FOREIGN KEY (nft_id) REFERENCES nft_records(id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_music_files_hash ON music_files(file_hash);
CREATE INDEX IF NOT EXISTS idx_nft_records_token_id ON nft_records(token_id);
CREATE INDEX IF NOT EXISTS idx_nft_records_contract ON nft_records(contract_address);
CREATE INDEX IF NOT EXISTS idx_nft_records_status ON nft_records(status);
CREATE INDEX IF NOT EXISTS idx_transactions_hash ON transactions(tx_hash);
CREATE INDEX IF NOT EXISTS idx_transactions_nft_id ON transactions(nft_id);
