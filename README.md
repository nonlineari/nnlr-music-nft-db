# NNLR Music NFT Database

A database system for managing local music files and their corresponding NFT metadata on the Avalanche blockchain for **Naked Nuras Loves Rave**.

## Overview

This project provides a comprehensive solution for:
- Indexing local music files with metadata
- Managing NFT information on the Avalanche blockchain
- Tracking ownership and transaction history
- Organizing music collections for NFT minting

**Experimental:** Dual-protocol support (Avalanche + NEAR) with "warpaint" artistic visual layer for non-linear creative NFTs. See [EXPERIMENTAL_NFT.md](EXPERIMENTAL_NFT.md).

## Project Structure

```
nnlr-music-nft-db/
├── src/
│   ├── schema.sql           # Database schema definition
│   ├── database.py          # Database connection management
│   └── avalanche_client.py  # Avalanche blockchain integration
├── near-stack/              # Experimental NEAR (NEP-171) + warpaint
│   ├── experimental-nft.js
│   └── package.json
├── scripts/
│   └── index_files.py       # File indexing script
├── examples/
│   └── experimental_nft_example.py
├── data/                    # Database storage directory
├── tests/                   # Test files
└── docs/                    # Additional documentation
```

## Setup

### Prerequisites

- Python 3.8 or higher
- SQLite3
- Node.js + near-api-js (for experimental NEAR)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd nnlr-music-nft-db
```

2. Install dependencies:
```bash
pip install -r requirements.txt
cd near-stack && npm install
```

3. Initialize the database:
```bash
python -c "from src.database import get_database; db = get_database(); db.initialize_schema()"
```

## Usage

### Indexing Local Music Files

To index music files from a directory:

```bash
python scripts/index_files.py /path/to/music/directory
```

Supported audio formats:
- MP3 (.mp3)
- WAV (.wav)
- FLAC (.flac)
- AAC (.aac)
- M4A (.m4a)
- OGG (.ogg)
- WMA (.wma)

### Database Operations

The database includes the following main tables:

- **music_files**: Stores local file information and metadata
- **music_metadata**: Extended metadata (artist, title, album, etc.)
- **nft_records**: NFT information linked to music files
- **transactions**: Avalanche transaction history
- **collections**: NFT collection management

### Avalanche Integration

The Avalanche client provides methods for:
- Minting NFTs on Avalanche
- Querying NFT metadata
- Tracking transaction history
- Managing ownership

Example usage:

```python
from src.avalanche_client import get_avalanche_client

client = get_avalanche_client(network="mainnet")
# Use client methods for blockchain operations
```

## Experimental NEAR + Warpaint

See EXPERIMENTAL_NFT.md for NEAR NEP-171 module and "warpaint" (non-linear artistic visual overlays for music NFTs, tying to blockcode/generative visuals).

Example:
```bash
cd near-stack
node -e '
  const { getExperimentalNearNFT } = require("./experimental-nft");
  // init and mintWithWarpaint etc.
'
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Database Schema

The database schema is defined in `src/schema.sql` and includes comprehensive tables for managing music files, NFT records, and blockchain transactions.

## Avalanche Network

This project is designed to work with the Avalanche blockchain:
- **Mainnet**: Production environment
- **Testnet**: Testing environment (Fuji testnet)
- **Local**: Local development network

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

Dual-licensed under MIT OR GPL-3.0-or-later. See LICENSE and COPYING files for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/nnlr-music-nft-db/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/nnlr-music-nft-db/discussions)
