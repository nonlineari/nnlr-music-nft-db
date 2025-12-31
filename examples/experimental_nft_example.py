"""
Experimental NFT Example: NEAR and Avalanche Integration

This example demonstrates:
1. Creating separate NEAR and Avalanche NFT clients
2. Minting NFTs on each protocol
3. Querying NFT data from both protocols
4. Cross-protocol NFT management

Note: This is experimental code. For production use:
- Validate all addresses and inputs
- Implement proper error handling
- Use testnet first before mainnet
- Protect private keys (use .env files)
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'near-stack'))

from experimental_avalanche_nft import get_experimental_avalanche_nft
from protocol_factory import ProtocolFactory, DualProtocolNFTManager, create_nft_manager


async def example_single_protocol():
    """Example: Working with a single protocol."""
    print("=" * 70)
    print("EXAMPLE 1: Single Protocol NFT Operations")
    print("=" * 70)
    
    # ───────────────────────────────────────────────────────────────
    # AVALANCHE: Create client and check balance
    # ───────────────────────────────────────────────────────────────
    print("\n📦 Initializing Avalanche NFT Client (Testnet)\n")
    
    try:
        # Create Avalanche client (no private key = read-only mode)
        avax_client = get_experimental_avalanche_nft(network='testnet')
        
        print("✓ Avalanche client ready")
        print(f"  Network: {avax_client.network}")
        print(f"  RPC URL: {avax_client.rpc_url}")
        
        # Example: Estimate gas for different operations
        print("\n💰 Gas Estimates (Avalanche Testnet):\n")
        
        gas_transfer = avax_client.estimate_gas('0x0000000000000000000000000000000000000000', 'transfer')
        gas_mint = avax_client.estimate_gas('0x0000000000000000000000000000000000000000', 'mint')
        
        print(f"Transfer NFT:   {gas_transfer.get('gas_estimate', 'N/A')} gas")
        print(f"Mint NFT:       {gas_mint.get('gas_estimate', 'N/A')} gas")
        
    except Exception as e:
        print(f"⚠ Avalanche initialization: {e}")
    
    # ───────────────────────────────────────────────────────────────
    # NEAR: Create client
    # ───────────────────────────────────────────────────────────────
    print("\n📦 Initializing NEAR NFT Client (Testnet)\n")
    
    try:
        from experimental_nft import getExperimentalNearNFT
        
        # Create NEAR client with a sample NFT contract
        near_client = getExperimentalNearNFT(
            network='testnet',
            nftContractId='example-nft.testnet'  # Example contract
        )
        
        print("✓ NEAR client ready")
        print(f"  Network: {near_client.config.networkId}")
        print(f"  NFT Contract: {near_client.nftContractId}")
        
    except Exception as e:
        print(f"⚠ NEAR initialization: {e}")


async def example_protocol_factory():
    """Example: Using the protocol factory."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Protocol Factory")
    print("=" * 70 + "\n")
    
    # ───────────────────────────────────────────────────────────────
    # Create clients via factory
    # ───────────────────────────────────────────────────────────────
    print("Creating clients via ProtocolFactory...\n")
    
    try:
        # Create Avalanche client
        avax = ProtocolFactory.create_client(
            'avalanche',
            network='testnet'
        )
        print("✓ Avalanche client created")
        
        # Create NEAR client
        near = ProtocolFactory.create_client(
            'near',
            network='testnet',
            nft_contract_id='example-nft.testnet'
        )
        print("✓ NEAR client created")
        
        # List supported protocols
        protocols = ProtocolFactory.list_supported_protocols()
        print(f"\nSupported protocols: {', '.join(protocols)}")
        
    except Exception as e:
        print(f"⚠ Factory error: {e}")


async def example_dual_protocol_manager():
    """Example: Using dual protocol manager."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Dual Protocol NFT Manager")
    print("=" * 70 + "\n")
    
    # ───────────────────────────────────────────────────────────────
    # Configuration for both protocols
    # ───────────────────────────────────────────────────────────────
    config = {
        'near': {
            'network': 'testnet',
            'nft_contract_id': 'example-nft.testnet'
        },
        'avalanche': {
            'network': 'testnet',
            # 'private_key': os.getenv('AVALANCHE_PRIVATE_KEY')  # Optional
        }
    }
    
    print("Initializing Dual Protocol Manager with config:\n")
    print(f"  NEAR Network: {config['near']['network']}")
    print(f"  NEAR Contract: {config['near']['nft_contract_id']}")
    print(f"  Avalanche Network: {config['avalanche']['network']}\n")
    
    try:
        manager = create_nft_manager(config)
        
        print("\n✓ Manager initialized")
        print(f"Active protocols: {manager.list_initialized_protocols()}\n")
        
        # Get individual clients
        print("Accessing individual protocol clients:\n")
        
        near_client = manager.get_client('near')
        avax_client = manager.get_client('avalanche')
        
        if near_client:
            print(f"✓ NEAR: {near_client.nftContractId}")
        if avax_client:
            print(f"✓ Avalanche: Network={avax_client.network}")
            
    except Exception as e:
        print(f"⚠ Manager error: {e}")


async def example_nft_operations():
    """Example: NFT operations (read-only demonstrations)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: NFT Operations")
    print("=" * 70 + "\n")
    
    print("Note: This demonstrates read-only operations.")
    print("Write operations (mint/transfer) require funded accounts.\n")
    
    try:
        from experimental_nft import getExperimentalNearNFT
        
        near_client = getExperimentalNearNFT(
            network='testnet',
            nftContractId='example-nft.testnet'
        )
        
        print("NEAR NFT Operations Available:\n")
        print("• mintNFT()                 - Mint a new NFT")
        print("• transferNFT()             - Transfer NFT to another account")
        print("• getNFTMetadata()          - Fetch NFT metadata")
        print("• getNFTOwner()             - Get NFT owner address")
        print("• getAccountNFTs()          - List all NFTs owned by account")
        print("• getNFTSupply()            - Get contract supply statistics")
        print("• getNFTTransferHistory()   - Query transfer history via indexer")
        print("• approveNFT()              - Approve account to transfer")
        print("• revokeNFTApproval()       - Revoke transfer approval\n")
        
    except Exception as e:
        print(f"⚠ Operations example: {e}")
    
    try:
        avax_client = get_experimental_avalanche_nft(network='testnet')
        
        print("Avalanche NFT Operations Available:\n")
        print("• mint_nft()                - Mint a new NFT")
        print("• transfer_nft()            - Transfer NFT to another address")
        print("• get_nft_owner()           - Get NFT owner address")
        print("• get_nft_balance()         - Get account NFT balance")
        print("• get_nft_metadata()        - Fetch NFT metadata")
        print("• verify_transaction()      - Verify transaction on-chain")
        print("• estimate_gas()            - Estimate gas costs")
        print("• get_account_balance()     - Get AVAX balance\n")
        
    except Exception as e:
        print(f"⚠ Avalanche operations: {e}")


async def example_music_nft_workflow():
    """Example: Music NFT workflow (conceptual)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Music NFT Workflow")
    print("=" * 70 + "\n")
    
    print("Conceptual workflow for minting music as NFT:\n")
    print("1️⃣  Index local music file:")
    print("   • Extract metadata (title, artist, duration)")
    print("   • Calculate file hash (deduplication)")
    print("   • Store in database\n")
    
    print("2️⃣  Create NFT metadata:")
    print("   • Title from music metadata")
    print("   • Media URI (IPFS, HTTP)")
    print("   • Description with artist info\n")
    
    print("3️⃣  Mint across protocols (optional):")
    print("   • NEAR: nft_mint() function call")
    print("   • Avalanche: ERC721 mint transaction\n")
    
    print("4️⃣  Track in database:")
    print("   • Store NFT contract address")
    print("   • Store token ID")
    print("   • Link to music_files table\n")
    
    print("5️⃣  Query ownership:")
    print("   • Check owner on NEAR/Avalanche")
    print("   • Query transfer history via indexer\n")
    
    # Sample NFT metadata for music
    sample_metadata = {
        'title': 'Example Music Track',
        'artist': 'Artist Name',
        'description': 'A music NFT representing original composition',
        'media': 'ipfs://QmXXXXXXXXXXXXX',  # IPFS hash
        'token_id': 'track_001',
        'duration': 240,  # seconds
        'genre': 'Electronic'
    }
    
    print("Sample Music NFT Metadata:")
    for key, value in sample_metadata.items():
        print(f"  {key}: {value}")


async def main():
    """Run all examples."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " EXPERIMENTAL NFT PROTOCOLS: NEAR & AVALANCHE ".center(68) + "║")
    print("╚" + "═" * 68 + "╝\n")
    
    try:
        # Run examples
        await example_single_protocol()
        await example_protocol_factory()
        await example_dual_protocol_manager()
        await example_nft_operations()
        await example_music_nft_workflow()
        
        print("\n" + "=" * 70)
        print("EXAMPLES COMPLETE")
        print("=" * 70)
        print("\nNext Steps:")
        print("1. Set up testnet accounts on NEAR and Avalanche")
        print("2. Fund with test tokens")
        print("3. Configure private keys in .env")
        print("4. Run actual mint/transfer operations")
        print("5. Query data via indexers\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
