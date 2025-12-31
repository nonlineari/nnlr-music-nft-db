"""Protocol factory for creating blockchain-specific NFT clients."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from experimental_avalanche_nft import get_experimental_avalanche_nft


class NFTProtocolBase(ABC):
    """Abstract base for protocol-specific NFT implementations."""
    
    def __init__(self, protocol: str, network: str):
        """Initialize protocol base.
        
        Args:
            protocol: Protocol name ('near' or 'avalanche')
            network: Network name (testnet, mainnet, etc.)
        """
        self.protocol = protocol
        self.network = network
    
    @abstractmethod
    async def mint_nft(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """Mint an NFT on the protocol."""
        pass
    
    @abstractmethod
    async def transfer_nft(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """Transfer an NFT on the protocol."""
        pass
    
    @abstractmethod
    async def get_nft_metadata(self, token_id: str) -> Optional[Dict[str, Any]]:
        """Get NFT metadata."""
        pass
    
    @abstractmethod
    async def get_nft_owner(self, token_id: str) -> Optional[str]:
        """Get NFT owner address."""
        pass
    
    @abstractmethod
    async def verify_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Verify a transaction."""
        pass


class ProtocolFactory:
    """Factory for creating protocol-specific NFT clients."""
    
    _clients = {}
    
    @staticmethod
    def create_client(protocol: str, **kwargs) -> 'NFTProtocolBase':
        """Create a protocol-specific NFT client.
        
        Args:
            protocol: Protocol type ('near' or 'avalanche')
            **kwargs: Protocol-specific configuration
            
        Returns:
            Protocol-specific NFT client
            
        Raises:
            ValueError: If protocol is not supported
        """
        protocol = protocol.lower()
        
        if protocol == 'avalanche':
            network = kwargs.get('network', 'testnet')
            private_key = kwargs.get('private_key')
            
            # Return Avalanche experimental NFT client
            return get_experimental_avalanche_nft(
                network=network,
                private_key=private_key
            )
        
        elif protocol == 'near':
            # NEAR client requires async init, return placeholder
            network = kwargs.get('network', 'testnet')
            nft_contract = kwargs.get('nft_contract_id')
            
            # Import here to avoid circular dependency
            from sys import path
            path.insert(0, '../near-stack')
            from experimental_nft import getExperimentalNearNFT
            
            return getExperimentalNearNFT(network=network, nftContractId=nft_contract)
        
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
    
    @staticmethod
    def get_cached_client(protocol: str, **kwargs) -> 'NFTProtocolBase':
        """Get or create a cached client instance.
        
        Args:
            protocol: Protocol type
            **kwargs: Configuration options
            
        Returns:
            Cached or new protocol client
        """
        cache_key = f"{protocol}_{kwargs.get('network', 'testnet')}"
        
        if cache_key not in ProtocolFactory._clients:
            ProtocolFactory._clients[cache_key] = ProtocolFactory.create_client(
                protocol, **kwargs
            )
        
        return ProtocolFactory._clients[cache_key]
    
    @staticmethod
    def clear_cache():
        """Clear all cached clients."""
        ProtocolFactory._clients.clear()
    
    @staticmethod
    def list_supported_protocols() -> list:
        """List supported blockchain protocols.
        
        Returns:
            List of supported protocol names
        """
        return ['near', 'avalanche']


class DualProtocolNFTManager:
    """Manager for working with both NEAR and Avalanche NFTs simultaneously."""
    
    def __init__(self):
        """Initialize dual protocol manager."""
        self.clients = {}
    
    def initialize(self, config: Dict[str, Any]):
        """Initialize clients for configured protocols.
        
        Args:
            config: Configuration dictionary with protocol settings
            
            Example:
                {
                    'near': {
                        'network': 'testnet',
                        'nft_contract_id': 'nft.myname.testnet'
                    },
                    'avalanche': {
                        'network': 'testnet',
                        'private_key': '0x...'
                    }
                }
        """
        for protocol, settings in config.items():
            protocol = protocol.lower()
            if protocol in ProtocolFactory.list_supported_protocols():
                self.clients[protocol] = ProtocolFactory.create_client(
                    protocol,
                    **settings
                )
                print(f"✓ {protocol.upper()} NFT client initialized")
            else:
                print(f"⚠ Unsupported protocol: {protocol}")
    
    async def mint_across_protocols(self, 
                                   protocols: list,
                                   metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Mint the same NFT across multiple protocols.
        
        Args:
            protocols: List of protocols to mint on ('near', 'avalanche')
            metadata: NFT metadata
            
        Returns:
            Dictionary with results for each protocol
        """
        results = {}
        
        for protocol in protocols:
            if protocol not in self.clients:
                results[protocol] = {
                    'success': False,
                    'error': f'Client not initialized for {protocol}'
                }
                continue
            
            try:
                client = self.clients[protocol]
                
                if protocol == 'near':
                    result = await client.mintNFT(
                        signerAccountId=metadata.get('signer_account'),
                        tokenId=metadata.get('token_id'),
                        receiverId=metadata.get('receiver_id'),
                        metadata={
                            'title': metadata.get('title'),
                            'description': metadata.get('description'),
                            'media': metadata.get('media')
                        }
                    )
                elif protocol == 'avalanche':
                    result = client.mint_nft(
                        contract_address=metadata.get('contract_address'),
                        to_address=metadata.get('to_address'),
                        metadata_uri=metadata.get('metadata_uri')
                    )
                
                results[protocol] = result if result else {
                    'success': False,
                    'error': 'Minting failed'
                }
            except Exception as e:
                results[protocol] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
    def get_client(self, protocol: str):
        """Get a protocol-specific client.
        
        Args:
            protocol: Protocol name
            
        Returns:
            Protocol client or None
        """
        return self.clients.get(protocol.lower())
    
    def list_initialized_protocols(self) -> list:
        """List initialized protocol clients.
        
        Returns:
            List of protocol names with active clients
        """
        return list(self.clients.keys())


def create_nft_manager(config: Dict[str, Any]) -> DualProtocolNFTManager:
    """Create and initialize a dual protocol NFT manager.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Initialized DualProtocolNFTManager
    """
    manager = DualProtocolNFTManager()
    manager.initialize(config)
    return manager
