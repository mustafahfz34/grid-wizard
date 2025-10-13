🧭 UI & Runtime

When you run `wizard_orchestrator_v2.py --ui`, you’ll see two main tabs:

### 🪄 Settings tab
Edit `.env` keys from the UI.  
- Saving here updates `.env` immediately.  
- The orchestrator hot-reloads it within seconds.

### 🚀 Run tab
Start and stop the trading loop.  
The console will stream key messages:

| Tag | Meaning |
|------|---------|
| `[OpenCap]` | Shows open vs pending offers and effective caps |
| `[Cycle]` | Summary after each loop: placed, skipped, throttle, pending, cancelled |
| `[BUY]` / `[SELL]` | Each placement with price and size |
| `[Cancel]` | Offer cancelled by auto-cancel or reserve-relief logic |
| `[NFT]` | License gate message |
