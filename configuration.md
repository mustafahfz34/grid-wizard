# 🔧 Configuration

Grid Wizard reads all runtime parameters from `.env` — but hot-reloads them automatically when the file changes.

### Key parameters

| Section | Key | Description |
|----------|-----|-------------|
| Grid | `MAX_OPEN_BUYS`, `MAX_OPEN_SELLS` | Maximum concurrent orders per side |
| Queue | `PENDING_TTL_SEC` | Pending order time-to-live (default 120s) |
| Throttles | `BUY_THROTTLE_SEC`, `SELL_THROTTLE_SEC` | Minimum seconds between placements per side |
| Auto-Cancel | `AUTO_CANCEL_ENABLED` | 1 = on, 0 = off |
| Auto-Cancel | `AUTO_CANCEL_BUY_BPS_FROM_MID`, `AUTO_CANCEL_SELL_BPS_FROM_MID` | Cancel farthest orders beyond this distance |
| Reserve Relief | `RESERVE_RELIEF_ENABLED` | Prune offers when object reserve high |
| Adaptive | `STEP_PCT` | Step % between grid levels |
| Tranche | `BUY_TRANCHE_RLUSD`, `SELL_TRANCHE_RLUSD` | Order size in RLUSD per side |

### Example snippet

MAX_OPEN_BUYS=12
MAX_OPEN_SELLS=2
BUY_OFFSET_BPS=2
SELL_OFFSET_BPS=5
STEP_PCT=0.5
PENDING_TTL_SEC=120
BUY_THROTTLE_SEC=10
SELL_THROTTLE_SEC=10
AUTO_CANCEL_ENABLED=1
