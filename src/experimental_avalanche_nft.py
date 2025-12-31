"""Experimental Avalanche NFT operations using web3.py."""

import os
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from web3 import Web3
from web3.contract import Contract
from web3.eth import Eth


class ExperimentalAvalancheNFT:
    """Experimental implementation for Avalanche NFT operations."""
    
    # Standard ERC721 ABI (minimal for minting and transfers)
    ERC721_ABI = [
        {
            "name": "balanceOf",
            "type": "function",
            "stateMutability": "view",
            "inputs": [{"name": "owner", "type": "address"}],
            "outputs": [{"name": "", "type": "uint256"}]
        },
        {
            "name": "ownerOf",
            "type": "function",
            "stateMutability": "view",
            "inputs": [{"name": "tokenId", "type": "uint256"}],
            "outputs": [{"name": "", "type": "address"}]
        },
        {
            "name": "safeTransferFrom",
            "type": "function",
            "stateMutability": "nonpayable",
            "inputs": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "tokenId", "type": "uint256"}
            ]
        },
        {
            "name": "transferFrom",
            "type": "function",
            "stateMutability": "nonpayable",
            "inputs": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "tokenId", "type": "uint256"}
            ]
        },
        {
            "name": "approve",
            "type": "function",
            "stateMutability": "nonpayable",
            "inputs": [
                {"name": "to", "type": "address"},
                {"name": "tokenId", "type": "uint256"}
            ]
        }
    ]
    
    def __init__(self, network: str = "testnet", private_key: Optional[str] = None):
        """Initialize Avalanche NFT client.
        
        Args:
            network: Network to connect to ('mainnet', 'testnet', or 'local')
            private_key: Private key for signing transactions (from .env if not provided)
        """
        self.network = network
        self.rpc_url = self._get_rpc_url(network)
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Load private key from environment if not provided
        self.private_key = private_key or os.getenv("AVALANCHE_PRIVATE_KEY")
        self.account_address = None
        
        if self.private_key:
            # Derive account from private key
            account = self.w3.eth.account.from_key(self.private_key)
            self.account_address = account.address
        
        # Verify connection
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to Avalanche {network} at {self.rpc_url}")
        
        print(f"✓ Connected to Avalanche {network}")
        if self.account_address:
            print(f"✓ Account: {self.account_address}")
    
    def _get_rpc_url(self, network: str) -> str:
        """Get RPC URL for the specified network.
        
        Args:
            network: Network name
            
        Returns:
            RPC endpoint URL
        """
        urls = {
            "mainnet": "https://api.avax.network/ext/bc/C/rpc",
            "testnet": "https://api.avax-test.network/ext/bc/C/rpc",
            "local": "http://localhost:9650/ext/bc/C/rpc"
        }
        return urls.get(network, urls["mainnet"])
    
    def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance in AVAX.
        
        Returns:
            Dictionary with balance information
        """
        if not self.account_address:
            raise ValueError("No account configured. Provide private_key.")
        
        balance_wei = self.w3.eth.get_balance(self.account_address)
        balance_avax = self.w3.from_wei(balance_wei, 'ether')
        
        return {
            "address": self.account_address,
            "balance_wei": balance_wei,
            "balance_avax": str(balance_avax)
        }
    
    def get_nft_owner(self, contract_address: str, token_id: int) -> Optional[str]:
        """Get the owner of an NFT.
        
        Args:
            contract_address: NFT contract address
            token_id: Token ID
            
        Returns:
            Owner address or None if not found
        """
        try:
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=self.ERC721_ABI
            )
            owner = contract.functions.ownerOf(token_id).call()
            return owner
        except Exception as e:
            print(f"Error fetching owner: {e}")
            return None
    
    def get_nft_balance(self, contract_address: str, account: Optional[str] = None) -> int:
        """Get NFT balance for an account.
        
        Args:
            contract_address: NFT contract address
            account: Account address (uses self.account_address if not provided)
            
        Returns:
            Number of NFTs owned
        """
        try:
            account = account or self.account_address
            if not account:
                raise ValueError("No account specified")
            
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=self.ERC721_ABI
            )
            balance = contract.functions.balanceOf(account).call()
            return balance
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return 0
    
    def mint_nft(self,
                 contract_address: str,
                 to_address: str,
                 metadata_uri: str,
                 token_id: Optional[int] = None,
                 gas: int = 500000,
                 gas_price_multiplier: float = 1.0) -> Optional[Dict[str, Any]]:
        """Mint a new NFT (requires contract supporting mint function).
        
        Args:
            contract_address: NFT contract address
            to_address: Recipient address
            metadata_uri: URI pointing to NFT metadata (IPFS or HTTP)
            token_id: Optional specific token ID
            gas: Gas limit
            gas_price_multiplier: Multiply current gas price by this factor
            
        Returns:
            Transaction receipt dictionary or None if failed
        """
        if not self.private_key:
            raise ValueError("Private key required for minting. Configure AVALANCHE_PRIVATE_KEY.")
        
        try:
            # Get current gas price and apply multiplier
            base_gas_price = self.w3.eth.gas_price
            gas_price = int(base_gas_price * gas_price_multiplier)
            
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(self.account_address)
            
            # Build transaction (simplified - actual contract may differ)
            # This is a generic template; real implementation depends on contract interface
            tx_data = {
                'from': self.account_address,
                'to': Web3.to_checksum_address(contract_address),
                'value': 0,
                'gas': gas,
                'gasPrice': gas_price,
                'nonce': nonce,
                'data': self.w3.keccak(text=f"mint:{to_address}:{metadata_uri}")[:4]  # Placeholder
            }
            
            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"Minting NFT... TX: {self.w3.to_hex(tx_hash)}")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            
            return {
                "tx_hash": self.w3.to_hex(tx_hash),
                "status": "success" if receipt['status'] == 1 else "failed",
                "block_number": receipt['blockNumber'],
                "gas_used": receipt['gasUsed'],
                "to_address": to_address,
                "metadata_uri": metadata_uri,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Minting error: {e}")
            return None
    
    def transfer_nft(self,
                    contract_address: str,
                    token_id: int,
                    to_address: str,
                    gas: int = 100000,
                    gas_price_multiplier: float = 1.0) -> Optional[Dict[str, Any]]:
        """Transfer an NFT to another address.
        
        Args:
            contract_address: NFT contract address
            token_id: Token ID to transfer
            to_address: Recipient address
            gas: Gas limit
            gas_price_multiplier: Multiply current gas price by this factor
            
        Returns:
            Transaction receipt dictionary or None if failed
        """
        if not self.private_key:
            raise ValueError("Private key required for transfers. Configure AVALANCHE_PRIVATE_KEY.")
        
        try:
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=self.ERC721_ABI
            )
            
            # Get current gas price and apply multiplier
            base_gas_price = self.w3.eth.gas_price
            gas_price = int(base_gas_price * gas_price_multiplier)
            
            # Build transfer transaction
            tx = contract.functions.transferFrom(
                self.account_address,
                Web3.to_checksum_address(to_address),
                token_id
            ).build_transaction({
                'from': self.account_address,
                'gas': gas,
                'gasPrice': gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account_address)
            })
            
            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"Transferring NFT #{token_id}... TX: {self.w3.to_hex(tx_hash)}")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            
            return {
                "tx_hash": self.w3.to_hex(tx_hash),
                "status": "success" if receipt['status'] == 1 else "failed",
                "block_number": receipt['blockNumber'],
                "gas_used": receipt['gasUsed'],
                "token_id": token_id,
                "from_address": self.account_address,
                "to_address": to_address,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Transfer error: {e}")
            return None
    
    def verify_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Verify a transaction on Avalanche.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction details dictionary or None if not found
        """
        try:
            # Ensure proper format
            if not tx_hash.startswith('0x'):
                tx_hash = f"0x{tx_hash}"
            
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            tx = self.w3.eth.get_transaction(tx_hash)
            
            if receipt:
                return {
                    "tx_hash": tx_hash,
                    "status": "confirmed" if receipt['status'] == 1 else "failed",
                    "block_number": receipt['blockNumber'],
                    "gas_used": receipt['gasUsed'],
                    "from": tx['from'],
                    "to": tx['to'],
                    "value": str(self.w3.from_wei(tx['value'], 'ether')),
                    "timestamp": datetime.now().isoformat()
                }
            return None
        except Exception as e:
            print(f"Verification error: {e}")
            return None
    
    def get_transaction_history(self, token_id: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get transaction history (requires external indexer or manual tracking).
        
        Args:
            token_id: Optional token ID to filter
            limit: Number of transactions to return
            
        Returns:
            List of transaction dictionaries
        """
        # Note: Full transaction history requires indexer or event log queries
        # This is a placeholder that would typically query an indexer service
        print("Transaction history requires integration with Avalanche indexer")
        print("Consider using services like Covalent or Snowtrace API")
        return []
    
    def estimate_gas(self, contract_address: str, function_name: str) -> Dict[str, Any]:
        """Estimate gas cost for NFT operation.
        
        Args:
            contract_address: NFT contract address
            function_name: Function to estimate gas for
            
        Returns:
            Gas estimation details
        """
        try:
            current_price = self.w3.eth.gas_price
            avax_price_wei = current_price
            
            # Estimate different operations
            estimates = {
                "transfer": 100000,
                "mint": 500000,
                "approve": 45000
            }
            
            gas_estimate = estimates.get(function_name, 100000)
            estimated_cost_wei = gas_estimate * avax_price_wei
            estimated_cost_avax = self.w3.from_wei(estimated_cost_wei, 'ether')
            
            return {
                "function": function_name,
                "gas_estimate": gas_estimate,
                "current_gas_price": str(self.w3.from_wei(current_price, 'gwei')),
                "estimated_cost_avax": str(estimated_cost_avax),
                "network": self.network
            }
        except Exception as e:
            print(f"Gas estimation error: {e}")
            return {}


def get_experimental_avalanche_nft(network: str = "testnet", private_key: Optional[str] = None) -> ExperimentalAvalancheNFT:
    """Get an experimental Avalanche NFT client instance.
    
    Args:
        network: Network to connect to
        private_key: Optional private key (falls back to environment)
        
    Returns:
        Configured ExperimentalAvalancheNFT instance
    """
    return ExperimentalAvalancheNFT(network, private_key)
