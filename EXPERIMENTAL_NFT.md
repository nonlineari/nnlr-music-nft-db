# Experimental NFT Protocol Modules

This document describes the experimental NEAR and Avalanche NFT modules created as separate, protocol-specific entities.

## Overview

Two independent NFT implementations allow experimentation with blockchain-specific operations:

- **Avalanche NFT Module** (`src/experimental_avalanche_nft.py`) - ERC721-based operations
- **NEAR NFT Module** (`../near-stack/experimental-nft.js`) - NEAR NEP-171 standard operations
- **Protocol Factory** (`src/protocol_factory.py`) - Unified interface for both protocols

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           Dual Protocol NFT Manager                          │
│  (src/protocol_factory.py - DualProtocolNFTManager)          │
└─────────────────┬──────────────────────┬────────────────────┘
                  │                      │
        ┌─────────▼──────┐     ┌─────────▼──────────┐
        │    NEAR NFT    │     │  Avalanche NFT     │
        │  (JS/Node.js)  │     │   (Python/web3.py) │
        └────────────────┘     └────────────────────┘
             ↓                           ↓
        NEAR Protocol              Avalanche C-Chain
        (testnet/mainnet)          (testnet/mainnet)
```

## Avalanche Experimental NFT Module

**File:** `src/experimental_avalanche_nft.py`

### Features

- Web3.py integration for Ethereum-compatible operations
- ERC721 standard support
- Account balance queries
- NFT ownership verification
- Minting with metadata URI
- NFT transfers between addresses
- Transaction verification
- Gas estimation for operations

### Class: ExperimentalAvalancheNFT

```python
from experimental_avalanche_nft import get_experimental_avalanche_nft

# Create client (read-only without private key)
client = get_experimental_avalanche_nft(network='testnet')

# With private key (for write operations)
client = get_experimental_avalanche_nft(
    network='testnet',
    private_key='0x...'
)
```

### Key Methods

#### Read Operations (No Private Key Required)

```python
# Get account balance
balance = client.get_account_balance()
# Returns: {'address': '0x...', 'balance_avax': '1.5', ...}

# Get NFT owner
owner = client.get_nft_owner(
    contract_address='0x...',
    token_id=1
)

# Get NFT balance for account
balance = client.get_nft_balance(
    contract_address='0x...',
    account='0x...'
)

# Verify transaction
receipt = client.verify_transaction(tx_hash='0x...')

# Estimate gas costs
estimate = client.estimate_gas(
    contract_address='0x...',
    function_name='transfer'  # or 'mint', 'approve'
)
```

#### Write Operations (Requires Private Key)

```python
# Mint NFT
result = client.mint_nft(
    contract_address='0x...',
    to_address='0x...',
    metadata_uri='ipfs://QmXXX',
    gas=500000,
    gas_price_multiplier=1.0
)

# Transfer NFT
result = client.transfer_nft(
    contract_address='0x...',
    token_id=1,
    to_address='0x...',
    gas=100000
)
```

### Configuration

```bash
# Set environment variables for private key
export AVALANCHE_PRIVATE_KEY=0x...
export AVALANCHE_NETWORK=testnet  # testnet or mainnet
```

### Network Configuration

- **Mainnet:** `https://api.avax.network/ext/bc/C/rpc`
- **Testnet:** `https://api.avax-test.network/ext/bc/C/rpc`
- **Local:** `http://localhost:9650/ext/bc/C/rpc`

## NEAR Experimental NFT Module

**File:** `../near-stack/experimental-nft.js`

### Features

- Extends NearClient with NFT-specific methods
- NEP-171 standard support
- Metadata caching for performance
- Transfer history via indexer queries
- Account approval system
- Supply statistics
- Integration with NEAR QueryAPI indexer

### Class: ExperimentalNearNFT

```javascript
const { getExperimentalNearNFT } = require('./experimental-nft');

// Create client
const client = getExperimentalNearNFT(
    network = 'testnet',
    nftContractId = 'nft.myname.testnet'
);

// Initialize (async)
await client.init(accountId, privateKey);
```

### Key Methods

#### Read Operations

```javascript
// Get NFT metadata
const metadata = await client.getNFTMetadata(tokenId);

// Get NFT owner
const owner = await client.getNFTOwner(tokenId);

// Get all NFTs for account
const nfts = await client.getAccountNFTs(accountId, limit=50);

// Get supply statistics
const supply = await client.getNFTSupply();
// Returns: { totalSupply, contractName, contractSymbol, ... }

// Get transfer history
const history = await client.getNFTTransferHistory(accountId, limit=10);

// Cache operations
const stats = client.getCacheStats();
client.clearCache();
```

#### Write Operations (Requires Account & Credentials)

```javascript
// Mint NFT
const result = await client.mintNFT({
    signerAccountId: 'account.testnet',
    tokenId: 'token_001',
    receiverId: 'recipient.testnet',
    metadata: {
        title: 'NFT Title',
        description: 'Description',
        media: 'https://...',
        reference: 'https://...'
    },
    deposit: '0.1'
});

// Transfer NFT
const result = await client.transferNFT({
    signerAccountId: 'account.testnet',
    tokenId: 'token_001',
    receiverId: 'new_owner.testnet',
    memo: 'Transfer memo'
});

// Approve account to transfer
const result = await client.approveNFT({
    signerAccountId: 'owner.testnet',
    tokenId: 'token_001',
    approvedAccountId: 'spender.testnet'
});

// Revoke approval
const result = await client.revokeNFTApproval({
    signerAccountId: 'owner.testnet',
    tokenId: 'token_001',
    approvedAccountId: 'spender.testnet'
});
```

## Protocol Factory

**File:** `src/protocol_factory.py`

Unified interface for creating and managing both protocols.

### Usage

```python
from protocol_factory import ProtocolFactory, create_nft_manager

# Single protocol creation
client = ProtocolFactory.create_client(
    'avalanche',
    network='testnet',
    private_key='0x...'
)

client = ProtocolFactory.create_client(
    'near',
    network='testnet',
    nft_contract_id='nft.testnet'
)

# Cached clients
client = ProtocolFactory.get_cached_client('avalanche', network='testnet')

# List supported
protocols = ProtocolFactory.list_supported_protocols()
# Returns: ['near', 'avalanche']
```

### Dual Protocol Manager

Manage both NEAR and Avalanche clients simultaneously:

```python
from protocol_factory import create_nft_manager

config = {
    'near': {
        'network': 'testnet',
        'nft_contract_id': 'nft.testnet'
    },
    'avalanche': {
        'network': 'testnet',
        'private_key': '0x...'
    }
}

manager = create_nft_manager(config)

# Get individual clients
near_client = manager.get_client('near')
avax_client = manager.get_client('avalanche')

# List active protocols
protocols = manager.list_initialized_protocols()
# Returns: ['near', 'avalanche']

# Mint across protocols
results = await manager.mint_across_protocols(
    ['near', 'avalanche'],
    {
        'token_id': 'music_001',
        'title': 'Song Title',
        'media': 'ipfs://QmXXX',
        # ... protocol-specific params
    }
)
```

## Integration Example

**File:** `examples/experimental_nft_example.py`

Run the example to see:
- Single protocol initialization
- Protocol factory usage
- Dual protocol manager setup
- Available operations
- Music NFT workflow concept

```bash
cd examples
python experimental_nft_example.py
```

## Music NFT Workflow

Conceptual workflow for minting music files as NFTs:

```
Music File
    ↓
Index & Extract Metadata (src/database.py)
    ├─ Extract: title, artist, duration, genre
    ├─ Calculate: SHA256 hash
    └─ Store: in music_files table
    ↓
Create NFT Metadata
    ├─ Title from music metadata
    ├─ Media URI (IPFS or HTTP)
    └─ Description with artist info
    ↓
Mint on Blockchain (experimental_nft modules)
    ├─ NEAR: nft_mint() → token_id + tx_hash
    └─ Avalanche: mint_nft() → tx_hash + token_id
    ↓
Track in Database (nft_records table)
    ├─ Store contract address
    ├─ Store token_id
    └─ Link to music_files
    ↓
Query & Verify (indexer + verify_transaction)
    ├─ Check current owner
    ├─ Query transfer history
    └─ Verify on-chain state
```

## Important Notes

### Security

- **Never commit private keys** - Use `.env` files (gitignored)
- **Validate addresses** before transactions
- **Test on testnet first** before mainnet
- **Use environment variables** for sensitive data

### Network Selection

```python
# Avalanche
client = get_experimental_avalanche_nft(network='mainnet')  # Production
client = get_experimental_avalanche_nft(network='testnet')  # Testing
client = get_experimental_avalanche_nft(network='local')    # Local dev

# NEAR
client = getExperimentalNearNFT(network='mainnet')   # Production
client = getExperimentalNearNFT(network='testnet')   # Testing
```

### Gas & Costs

**Avalanche:**
- Transfer: ~100,000 gas
- Mint: ~500,000 gas
- Use `estimate_gas()` for current costs

**NEAR:**
- Transaction cost: ~0.1 NEAR
- Storage deposit: 0.1 NEAR per transfer
- Methods use 30 TGas (compute)

## Prerequisites

### Python (Avalanche)

```bash
pip install web3>=6.0.0
```

### JavaScript (NEAR)

```bash
npm install near-api-js
```

## Testing

Both modules include error handling and logging:

```python
# Python
try:
    result = client.mint_nft(...)
except ValueError as e:
    print(f"Validation error: {e}")
except ConnectionError as e:
    print(f"Network error: {e}")

# JavaScript
try {
    const result = await client.mintNFT({...});
} catch (error) {
    console.error('Mint error:', error.message);
}
```

## Warpaint Concept (NEAR Artistic Layer)

**Added in near-stack/experimental-nft.js**

"Warpaint" extends NEAR NFTs with non-linear, artistic visual overlays inspired by the project's creative ethos (nonlineari / NLS / blockcode / anti-lingual visuals).

- Generative warpaint metadata: style, colors, patterns (e.g., blockcode, non-linear flows).
- `mintWithWarpaint()` helper for music NFTs with visual "paint" layer.
- Ties to music visuals, VJing, generative art in related projects (clive, NNLR, Renoise, etc.).
- Example:
  ```js
  const result = await client.mintWithWarpaint({
    ...baseMintParams,
    warpaint: {
      style: 'not-so-linear',
      colors: ['#c0a', '#f0f', '#0ff'],
      pattern: 'blockcode-cube',
      description: 'H - G 2001 IC SKD random cell stuffing visual'
    }
  });
  ```

See the JS implementation for full details and integration with the music NFT workflow.

## Future Enhancements

- [x] Warpaint visual layer for NEAR NFTs
- [ ] Batch operations (mint multiple NFTs)
- [ ] Event listeners for transfers
- [ ] Collection management
- [ ] Royalty tracking
- [ ] Integration with IPFS pinning
- [ ] Automated metadata backup
- [ ] Cross-chain bridging
- [ ] Marketplace integration
- [ ] Warpaint generator using local clive/NNLR tools

## References

- [NEAR NEP-171 (NFT Standard)](https://github.com/near/NEPs/blob/master/neps/nep-0171.md)
- [Avalanche ERC721 Documentation](https://docs.avax.network)
- [web3.py Documentation](https://web3py.readthedocs.io/)
- [near-api-js Documentation](https://near.github.io/near-api-js/)

## Support

For experimental features:
1. Test thoroughly on testnet
2. Report issues with minimal reproducible examples
3. Refer to protocol-specific documentation
4. Validate all blockchain addresses
