install.md
# ⚙️ Installation

## Requirements
- Python 3.10+  
- `pip` package manager  
- Internet connection to an XRPL node (public or private)

## 1. Clone the repository

git clone https://github.com/terramike/grid-wizard.git
cd grid-wizard

2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Configure your environment

Copy the example file and edit your wallet info:

cp examples/.env.example .env


⚠️ Never commit .env — it contains private keys.
.gitignore already protects it.

5. Run the UI
python wizard_orchestrator_v2.py --ui


# Additional Info:
**`INSTALL.md`** 


# The Grid Wizard — Installation Guide (Windows)

Welcome to **Grid Wizard Labs**. This guide covers installing the Windows EXE/Installer, first-run wallet setup, safe defaults, and common troubleshooting.

> **TL;DR:** Install → open app → paste **CLASSIC_ADDRESS** + **PRIVATE_KEY_HEX** → **Save Settings** → set caps ≥ 1 when ready.



## 1) System Requirements

- **OS:** Windows 10/11 (64-bit)
- **Disk:** ~300 MB free
- **Network:** Stable internet to reach XRPL RPC (s1/s2.ripple.com by default)
- **Wallet:** XRPL “Classic Address” + **secp256k1** private key (hex)

> macOS/Linux users can run from source (`python`), but this doc focuses on Windows EXE.



## 2) Download

1. Go to **Releases**:  
   **https://github.com/terramike/grid-wizard/releases/latest**
2. Choose one:
   - **Installer (recommended):** `GridWizard-Setup-vX.Y.Z.exe`
   - **Portable EXE:** `GridWizard.exe` (no install)

Optional: verify file integrity (see **Checksums** below).



## 3) Install / Launch

### Option A — Installer (recommended)
1. Run `GridWizard-Setup-vX.Y.Z.exe`.
2. Accept defaults; a Start Menu shortcut is created.
3. Launch **The Grid Wizard** from Start Menu/desktop.

### Option B — Portable EXE
1. Place `GridWizard.exe` anywhere you like.
2. Double-click to run.

> The app opens a black console and a Tk UI window. Logs print to the console and to the in-app log panel.



## 4) First-Run Behavior (Safe by Default)

- The bot **starts idle**:  
  `MAX_OPEN_BUYS=0` and `MAX_OPEN_SELLS=0`.
- **Hot-reload** checks `.env` every **30s**.
- On first run, if your wallet fields are blank, the loop **waits 30s** and **does not wipe UI inputs** while you paste keys.



## 5) Wallet Setup

You need:
- **CLASSIC_ADDRESS** (starts with `r...`)
- **PRIVATE_KEY_HEX** (secp256k1)

**Recommended wallet:** Bifrost (mobile)
- Export private key (Advanced → Export Private Key).
- Copy/paste carefully; do not store online.

> **Security:** The app never transmits your key anywhere except to sign XRPL transactions locally.



## 6) Configure the App

1. Open **The Grid Wizard**.
2. Go to **Settings** (right panel).
3. Paste:
   - `CLASSIC_ADDRESS` → your XRPL address (`r...`)
   - `PRIVATE_KEY_HEX` → your exported private key (hex)
   - Leave `KEY_ALGO=secp256k1`
4. Click **Save Settings**.
5. Watch the log:
   - You should see balances and “Waiting for next cycle…” messages.

### Where is `.env` stored?
- **Windows:** `%APPDATA%\GridWizard\.env`
- Click **Open Config Folder** in the UI to jump there.



## 7) Arming the Bot (Enable Trading)

When you’re ready:
1. Set caps above zero, e.g.:
   - `MAX_OPEN_BUYS=1`
   - `MAX_OPEN_SELLS=1`
2. (Optional) Tweak grid params (see quick defaults below).
3. Click **Save Settings**. Within ~30s the cycle will place orders as appropriate.

### Useful defaults (already set)
- `ENV_RELOAD_EVERY_SEC=30`
- `STEP_PCT=0.5` (grid spacing)
- `LEVELS=3`
- `BUY_OFFSET_BPS=6`, `SELL_OFFSET_BPS=6`
- `BUY_TRANCHE_RLUSD=10`, `SELL_TRANCHE_RLUSD=10`
- `AUTO_CANCEL_ENABLED=1` (distance recentering on)
- `SAFETY_BUFFER_XRP=60` (kept aside for reserves/fees)



## 8) Understanding Key Settings (quick reference)

| Key | Meaning |
|---|---|
| `MAX_OPEN_BUYS`, `MAX_OPEN_SELLS` | Caps on simultaneous open orders (set ≥1 to trade) |
| `STEP_PCT` | % spacing between grid levels (0.5 = 0.5%) |
| `LEVELS` | Number of grid rungs per side |
| `BUY/SELL_OFFSET_BPS` | Distance from mid for the closest rung (bps) |
| `BUY/SELL_TRANCHE_RLUSD` | RLUSD size per order |
| `MIN_NOTIONAL_RLUSD` | Min notional per order |
| `AUTO_CANCEL_ENABLED` | If `1`, cancels offers too far from mid |
| `RESERVE_RELIEF_ENABLED` | Optional pruning when object reserves are high |
| `PENDING_TTL_SEC`, `BUY/SELL_THROTTLE_SEC` | Queue/lag protections |

Full keys:  
📖 **Understanding Your .env** → https://github.com/terramike/grid-wizard/wiki/Understanding-Your-.env-File

AI section:  
🧠 **AI Hybrid Controls** → same page, Section “AI Hybrid Controls”



## 9) Updating

1. Download the new installer/EXE from **Releases**.
2. Close the app and replace the EXE (or run the new installer).
3. Your `.env` and logs stay in `%APPDATA%\GridWizard\`.



## 10) Uninstall

- **Installer build:** Use **Add/Remove Programs** → *The Grid Wizard*.
- **Portable EXE:** Delete the file.
- (Optional) Remove `%APPDATA%\GridWizard\` to clear `.env` and logs.



## 11) Troubleshooting

**Wallet not set / fields reset**  
- Fixed in v2+: setup loop waits 30s and doesn’t reload UI until keys are saved.
- Paste keys → **Save Settings**.

**`txnNotFound`**  
- XRPL node lag. The bot queues safely and confirms in subsequent cycles.

**No orders placed**  
- Ensure caps ≥ 1.  
- Check spendable XRP after `SAFETY_BUFFER_XRP` and XRPL reserves.

**Can’t find `.env`**  
- Click **Open Config Folder** in the UI.  
- Or check `%APPDATA%\GridWizard\.env`.

**SmartScreen warning**  
- First releases may trigger reputation prompts. You can **Run anyway** or code-sign future builds.



## 12) Verifying Downloads (optional)

Generate or download a `SHA256SUMS.txt` and verify:


# PowerShell
Get-FileHash .\GridWizard-Setup-vX.Y.Z.exe -Algorithm SHA256
Get-FileHash .\GridWizard.exe -Algorithm SHA256


Compare against the published checksums in the release.



## 13) Security & Privacy

* Keys are **local-only**; used to sign transactions to XRPL.
* No telemetry by default.
* Share logs only if you choose; redact addresses if needed.

Commercial/NFT licensing:
🪄 [https://xrp.cafe/usercollection/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/42000](https://xrp.cafe/usercollection/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/42000)



## 14) Helpful Links

* 🌐 **Repo:** [https://github.com/terramike/grid-wizard](https://github.com/terramike/grid-wizard)
* 📘 **Wiki Home:** [https://github.com/terramike/grid-wizard/wiki](https://github.com/terramike/grid-wizard/wiki)
* 🧭 **Install & Wallet Setup:** [https://github.com/terramike/grid-wizard/wiki/Installation-and-Wallet-Setup](https://github.com/terramike/grid-wizard/wiki/Installation-and-Wallet-Setup)
* 📖 **Understanding Your .env:** [https://github.com/terramike/grid-wizard/wiki/Understanding-Your-.env-File](https://github.com/terramike/grid-wizard/wiki/Understanding-Your-.env-File)
* 🪄 **License Mint (NFT):** [https://xrp.cafe/usercollection/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/42000](https://xrp.cafe/usercollection/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/42000)
* 🌳 **Linktree:** [https://linktr.ee/terramike](https://linktr.ee/terramike)
* 🕊️ **X (Twitter):** [https://x.com/nfterramike](https://x.com/nfterramike)



## 15) FAQ (quick)

**Q: Will the bot place trades immediately?**
A: No. Caps are `0/0` by default. Raise them when ready.

**Q: Does the app need admin rights?**
A: No. Standard user permissions are fine.

**Q: Can I edit `.env` directly?**
A: Yes, but using the **Settings** tab is safer. The app auto-reloads every 30s.

**Q: Where are logs?**
A: In the same folder as `.env` (`%APPDATA%\GridWizard\`), e.g., `profits.log`.



© Grid Wizard Labs

