# Grid Wizard Commercial License

Copyright © 2025 Grid Wizard Labs
Las Vegas, Nevada, USA  
All rights reserved.

---

## Overview

The **Grid Wizard Commercial License** grants permission to use the Grid Wizard
software in **production**, **automated trading**, or **revenue-generating**
contexts, provided the user holds a valid license NFT or written agreement
with Grid Wizard Labs.

The base source code is distributed under the **Business Source License 1.1 (BUSL-1.1)**,
which allows personal, educational, and security-audit use.  
Any **commercial or production use** requires this additional license.

---

## How to Obtain a Commercial License

### Option 1 – NFT License (on-chain verification)
Purchase or hold a **Grid Wizard Pro XRP NFT License** minted on the XRP Ledger.  
This NFT acts as your perpetual, verifiable proof of commercial rights.

**Mint / Marketplace Link:**  
🔗 <https://xrp.cafe/usercollection/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/42000>

**Verification Process (built-in):**
- On startup, the Grid Wizard software checks the connected XRPL wallet
  for an NFT issued by Grid Wizard Labs.  
- The NFT metadata must contain `license_type: "Pro"` or equivalent traits.  
- When verified, the software unlocks the **Pro features** such as:
  - Full grid-placement and cancellation automation  
  - Dynamic/Adaptive tranche sizing  
  - Reserve-relief and metrics modules  
  - Hot-reload tuning and UI control access  

Users can review this check directly in the public source
(`wizard_rlusd_grid_v2.py`, section `check_nft_license`), confirming that
no hidden logic or remote calls exist.

---

### Option 2 – Written Commercial Agreement
Organizations requiring custom terms (e.g., multi-wallet deployments,
white-label builds, or enterprise integrations) may obtain a separate
written license.

Contact → **licensing@gridwizard.dev**

---

## Rights Granted by a Commercial License

- Unlimited internal and production use of Grid Wizard software  
- Permission to run, modify, and extend the code for business use  
- Eligibility for private support and update notifications  
- Optional listing on the official “Verified Operators” page  

---

## Restrictions

Without a valid commercial license (NFT or contract), you may **not**:

- Use the software to execute, automate, or profit from live trades  
- Offer the software as a service or integrate it into a paid product  
- Represent yourself as an official or authorized operator  

Violations may result in revocation of license rights and, where applicable,
on-chain blacklisting of the associated NFT license.

---

## Governing Law

This License shall be governed by and construed in accordance with the
laws of the **State of Nevada, USA**, without regard to its conflict-of-law principles.

---

*For questions, bulk licensing, or NFT verification assistance, contact:*  
📧 licensing@gridwizard.dev
