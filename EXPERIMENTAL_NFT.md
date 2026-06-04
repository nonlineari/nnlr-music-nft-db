... (previous content) ...

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

... (rest of previous content) ...