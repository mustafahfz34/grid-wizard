# 🔐 Licensing

Grid Wizard is released under the **Business Source License 1.1 (BUSL-1.1)** with an NFT-based user license system.

---

## 1️⃣ Source Availability (BUSL-1.1)

You can read and audit the source for education and security review.  
You may not redistribute or offer it as a service.  
After **Jan 1 2028**, it converts to **Apache-2.0**.

---

## 2️⃣ NFT License = Software Key

To *run* Grid Wizard for live trading or production use, you must own a **Grid Wizard NFT License**.

**Issuer:** `rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52`  
**Mint Link:** [View on XRP.cafe](https://xrp.cafe/usercollection/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/42000)

When the software detects an NFT from this issuer in your wallet, it unlocks the Pro runtime.

---

## 3️⃣ What the NFT License Allows

✅ Install and run Grid Wizard for your own use  
✅ Receive updates and support while you hold the NFT  
✅ Transfer your license by transferring the NFT

🚫 No right to reproduce, modify, rebrand, resell, or redistribute the software  
🚫 No right to bundle Grid Wizard into other products or offer it as a service  

---

## 4️⃣ Verification Flow

1. On startup, the bot checks your wallet NFTs.  
2. If any NFT issuer matches the hard-coded address → license verified.  
3. If none found → runs in restricted mode (free edition).  

Transparent logic lives in [`wizard_license.py`](../wizard_license.py).

---

## 5️⃣ Revocation and Transfers
Licenses are verifiable on-chain and can be transferred by sending the NFT to a new wallet.  
Grid Wizard Labs may revoke NFTs used fraudulently or in violation of terms.
