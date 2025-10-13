# The Grid Wizard v2 (XRP/RLUSD)

Source-available grid trader for XRP/RLUSD with **strict caps + pending queue**, **side throttles**, **toggleable auto-cancel**, and optional **reserve relief**.

> License: Business Source License 1.1 (BUSL-1.1). Non-commercial/research permitted;  (e.g., Grid Wizard Pro NFT). See LICENSE and NFT-LICENSE.md.

## Quickstart
1. `python -m venv .venv && . .venv/bin/activate` (or Windows equivalent)
2. `pip install -r requirements.txt`
3. Copy `examples/.env.example` → `.env` and fill values.
4. `python wizard_orchestrator_v2.py --ui`

## Transparency
- Active settings are printed every cycle.
- Orders/cancels include sequence IDs, size, and price.
- NFT license logic is visible in code and checks only issuer/traits.

## Docs
See the GitBook: 

