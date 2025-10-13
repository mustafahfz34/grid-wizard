# 🛡 Security & Audit

Grid Wizard was designed for transparency and self-custody safety.

### No hidden network calls
- Connects only to XRPL public nodes and IPFS (for NFT metadata if queried).
- No telemetry, trackers, or remote control endpoints.

### What the bot can access
- Your configured wallet (address + private key from `.env`)
- XRPL data (account lines, offers, NFTs)
- No external exchanges or custodial APIs

### How to verify integrity
1. Inspect source: `wizard_rlusd_grid_v2.py`, `wizard_orchestrator_v2.py`, `wizard_license.py`
2. Check the **hard-coded issuer address**
3. Review the **license gate logic**
4. Compare your build’s hash to the official release tag on GitHub

### Security best practices
- Use a **dedicated wallet** with limited funds
- Never reuse private keys
- Rotate keys periodically
- Keep `.env` private and backed up offline

### Audits
Community audits and independent reviews are encouraged.  
Submit findings via [GitHub Issues](https://github.com/terramike/grid-wizard/issues).
