/**
 * Experimental NEAR NFT Module
 * NEP-171 standard support for music NFTs on NEAR Protocol.
 * Part of nnlr-music-nft-db experimental dual-protocol setup.
 *
 * "warpaint" concept: Visual/artistic "paint" layer for NFTs - e.g., generative
 * visual overlays, warpaint-style metadata for music visuals (tying to user's
 * visual/audio/code milieu, blockcode, non-linear creative work).
 *
 * Usage:
 *   const { getExperimentalNearNFT } = require('./experimental-nft');
 *   const client = getExperimentalNearNFT({ network: 'testnet', nftContractId: 'nft.testnet' });
 *   await client.init('account.testnet', 'ed25519:...');
 */

const { connect, keyStores, Contract } = require('near-api-js');
const fs = require('fs');
const path = require('path');

class ExperimentalNearNFT {
  constructor(config = {}) {
    this.network = config.network || 'testnet';
    this.nftContractId = config.nftContractId || 'nft.testnet';
    this.near = null;
    this.account = null;
    this.contract = null;
    this.metadataCache = new Map();
    this.config = {
      nodeUrl: this.network === 'mainnet' 
        ? 'https://rpc.mainnet.near.org' 
        : 'https://rpc.testnet.near.org',
      networkId: this.network,
      ...config
    };
  }

  async init(accountId, privateKey) {
    if (!accountId) throw new Error('accountId required');

    const keyStore = new keyStores.InMemoryKeyStore();
    if (privateKey) {
      // For simplicity, assume private key is in format for keyStore
      // In practice use near-api-js key pair
      const { KeyPair } = require('near-api-js');
      const keyPair = KeyPair.fromString(privateKey);
      await keyStore.setKey(this.config.networkId, accountId, keyPair);
    }

    this.near = await connect({
      ...this.config,
      keyStore,
    });

    this.account = await this.near.account(accountId);

    this.contract = new Contract(this.account, this.nftContractId, {
      viewMethods: [
        'nft_metadata',
        'nft_token',
        'nft_tokens_for_owner',
        'nft_total_supply',
        'nft_supply_for_owner',
      ],
      changeMethods: [
        'nft_mint',
        'nft_transfer',
        'nft_approve',
        'nft_revoke',
      ],
    });

    console.log(`NEAR NFT client initialized for ${this.nftContractId} on ${this.network}`);
  }

  // --- Read Operations ---

  async getNFTMetadata(tokenId) {
    if (this.metadataCache.has(tokenId)) {
      return this.metadataCache.get(tokenId);
    }
    const metadata = await this.contract.nft_token({ token_id: tokenId });
    if (metadata) {
      this.metadataCache.set(tokenId, metadata);
    }
    return metadata;
  }

  async getNFTOwner(tokenId) {
    const token = await this.getNFTMetadata(tokenId);
    return token ? token.owner_id : null;
  }

  async getAccountNFTs(accountId, limit = 50) {
    const tokens = await this.contract.nft_tokens_for_owner({
      account_id: accountId,
      from_index: '0',
      limit: limit.toString(),
    });
    return tokens || [];
  }

  async getNFTSupply() {
    const total = await this.contract.nft_total_supply();
    return {
      totalSupply: total,
      contractName: this.nftContractId,
      // Add more stats via indexer if needed
    };
  }

  async getNFTTransferHistory(accountId, limit = 10) {
    // Uses NEAR QueryAPI or indexer for transfer history
    // Placeholder - in real use, query https://api.nearblocks.io or indexer
    console.warn('getNFTTransferHistory: Implement with real indexer for production (e.g. NEAR QueryAPI)');
    return [];
  }

  getCacheStats() {
    return { size: this.metadataCache.size };
  }

  clearCache() {
    this.metadataCache.clear();
  }

  // --- Write Operations (require init with credentials) ---

  async mintNFT(params) {
    const { signerAccountId, tokenId, receiverId, metadata, deposit = '0.1' } = params;
    if (!this.account) throw new Error('Call init() with credentials first');

    const args = {
      token_id: tokenId,
      receiver_id: receiverId,
      token_metadata: metadata, // { title, description, media, reference, ... }
    };

    const result = await this.account.functionCall({
      contractId: this.nftContractId,
      methodName: 'nft_mint',
      args,
      gas: '300000000000000', // 300 TGas
      attachedDeposit: deposit, // in yoctoNEAR as string
    });

    return {
      success: true,
      tokenId,
      txHash: result.transaction.hash,
      result,
    };
  }

  async transferNFT(params) {
    const { signerAccountId, tokenId, receiverId, memo = '' } = params;
    if (!this.account) throw new Error('Call init() with credentials first');

    const args = {
      token_id: tokenId,
      receiver_id: receiverId,
      memo,
    };

    const result = await this.account.functionCall({
      contractId: this.nftContractId,
      methodName: 'nft_transfer',
      args,
      gas: '300000000000000',
      attachedDeposit: '1', // 1 yocto for security
    });

    return { success: true, txHash: result.transaction.hash };
  }

  async approveNFT(params) {
    const { signerAccountId, tokenId, approvedAccountId, msg = '' } = params;
    if (!this.account) throw new Error('Call init() with credentials first');

    const result = await this.account.functionCall({
      contractId: this.nftContractId,
      methodName: 'nft_approve',
      args: { token_id: tokenId, account_id: approvedAccountId, msg },
      gas: '300000000000000',
      attachedDeposit: '1',
    });

    return { success: true, txHash: result.transaction.hash };
  }

  async revokeNFTApproval(params) {
    const { signerAccountId, tokenId, approvedAccountId } = params;
    if (!this.account) throw new Error('Call init() with credentials first');

    const result = await this.account.functionCall({
      contractId: this.nftContractId,
      methodName: 'nft_revoke',
      args: { token_id: tokenId, account_id: approvedAccountId },
      gas: '300000000000000',
      attachedDeposit: '1',
    });

    return { success: true, txHash: result.transaction.hash };
  }

  // Warpaint concept integration example:
  // Add visual "warpaint" layer to NFT metadata for generative visuals
  // e.g., for music NFTs, attach warpaint SVG or description for visual "painting"
  async mintWithWarpaint(params) {
    const { ...baseParams, warpaint = { style: 'non-linear', colors: ['#c0a', '#f0f'], pattern: 'blockcode' } } = params;
    const metadata = {
      ...baseParams.metadata,
      warpaint, // NEAR concepts + warpaint visual layer
      extra: 'not-so-linear artistic overlay for the music NFT',
    };
    return this.mintNFT({ ...baseParams, metadata });
  }
}

/**
 * Factory function as described in EXPERIMENTAL_NFT.md
 */
function getExperimentalNearNFT(config) {
  return new ExperimentalNearNFT(config);
}

module.exports = {
  ExperimentalNearNFT,
  getExperimentalNearNFT,
};
