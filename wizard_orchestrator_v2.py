#!/usr/bin/env python3
"""
The Grid Wizard Orchestrator v2 – Runner + Tk UI + Env Hot-Reload + Metrics Hooks

This build:
- First-run .env bootstrap with safe defaults (wallet blanks)
- Robust parsing (blanks never crash: safe_int/safe_dec)
- UI shows defaults as hints and pre-fills empty entries
- Save Settings writes a complete .env with defaults for any blanks
- Defaults: ENV_RELOAD_EVERY_SEC=30, MAX_OPEN_BUYS=0, MAX_OPEN_SELLS=0
- Removed legacy LICENSE_NFT_ISSUER (license is hardcoded elsewhere if used)
- Fixed manage_grid_once arg: min_notional_rlusd -> min_notional
- UX FIX: During setup (wallet not configured), loop sleeps 30s and DOES NOT hot-reload UI fields
"""

import argparse
import os
import sys
import time
import subprocess
from decimal import Decimal, InvalidOperation
from typing import Optional
from threading import Thread, Event

import tkinter as tk
from tkinter import ttk, scrolledtext

from dotenv import load_dotenv
from xrpl.utils import drops_to_xrp

from config_manager import ensure_env_exists
from wizard_rlusd_grid_v2 import (
    manage_grid_once, load_wallet_from_env, connect_clients, healthy_client,
    get_balance_xrp, get_iou_balance, get_reserves_xrp, get_account_objects_count, fetch_orderbook_prices
)
from wizard_metrics import log_balances_and_stats

D = Decimal

# =========================
# Helpers
# =========================
def safe_int(v, default: int) -> int:
    try:
        s = ("" if v is None else str(v)).strip()
        return int(s) if s != "" else int(default)
    except Exception:
        return int(default)

def safe_dec(v, default: str | float | int) -> D:
    try:
        s = ("" if v is None else str(v)).strip()
        return D(s) if s != "" else D(default)
    except (InvalidOperation, ValueError):
        return D(default)

def dict_with_defaults(env: dict) -> dict:
    # Provide defaults for keys the engine expects (wallet fields may be blank)
    defaults = {
        "KEY_ALGO": "secp256k1",
        "RLUSD_ISSUER": "rMxCKbEDwqr76QuheSUMdEGf4B9xJ8m5De",
        "RLUSD_CURRENCY_CODE": "RLUSD",
        "XRPL_RPC_PRIMARY": "https://s1.ripple.com:51234",
        "XRPL_RPC_FALLBACK": "https://s2.ripple.com:51234",
        "MAX_OPEN_BUYS": "0",    # safe default (idle)
        "MAX_OPEN_SELLS": "0",   # safe default (idle)
        "BUY_OFFSET_BPS": "6",
        "SELL_OFFSET_BPS": "6",
        "STEP_PCT": "0.5",
        "BUY_TRANCHE_RLUSD": "10",
        "SELL_TRANCHE_RLUSD": "10",
        "MIN_NOTIONAL_RLUSD": "10",
        "SAFETY_BUFFER_XRP": "60",
        "GLOBAL_SL_RLUSD": "0",
        "SL_DISCOUNT_BPS": "10",
        "INTERVAL": "60",
        "LEVELS": "3",
        "AUTO_CANCEL_ENABLED": "1",
        "AUTO_CANCEL_BUY_BPS_FROM_MID": "150",
        "AUTO_CANCEL_SELL_BPS_FROM_MID": "150",
        "AUTO_CANCEL_MAX_PER_CYCLE": "1",
        "AUTO_CANCEL_STRATEGY": "farthest",
        "RESERVE_RELIEF_ENABLED": "0",
        "RESERVE_RELIEF_BUY_CAP": "10",
        "RESERVE_RELIEF_SELL_CAP": "2",
        "RESERVE_RELIEF_MAX_PER_CYCLE": "3",
        "RESERVE_RELIEF_GRACE_BPS": "8",
        "RESERVE_RELIEF_STRATEGY": "farthest",
        "PENDING_TTL_SEC": "120",
        "BUY_THROTTLE_SEC": "10",
        "SELL_THROTTLE_SEC": "10",
        "PRICE_FETCH_RETRIES": "3",
        "ENV_RELOAD_EVERY_SEC": "30",  # slower default
    }
    out = {**defaults, **env}
    # Wallet fields may legitimately be blank:
    out.setdefault("CLASSIC_ADDRESS", env.get("CLASSIC_ADDRESS", "").strip())
    out.setdefault("PRIVATE_KEY_HEX", env.get("PRIVATE_KEY_HEX", "").strip())
    return out

# =========================
# Resolve and load .env
# =========================
ENV_PATH = ensure_env_exists()
load_dotenv(dotenv_path=ENV_PATH, override=True)

def load_env() -> dict:
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    allowed = {
        "CLASSIC_ADDRESS", "PRIVATE_KEY_HEX", "KEY_ALGO",
        "RLUSD_ISSUER", "RLUSD_CURRENCY_CODE",
        "XRPL_RPC_PRIMARY", "XRPL_RPC_FALLBACK",
        "MAX_OPEN_BUYS", "MAX_OPEN_SELLS",
        "BUY_OFFSET_BPS", "SELL_OFFSET_BPS",
        "STEP_PCT", "BUY_TRANCHE_RLUSD", "SELL_TRANCHE_RLUSD",
        "MIN_NOTIONAL_RLUSD", "SAFETY_BUFFER_XRP",
        "GLOBAL_SL_RLUSD", "SL_DISCOUNT_BPS",
        "INTERVAL", "LEVELS",
        "AUTO_CANCEL_ENABLED", "AUTO_CANCEL_BUY_BPS_FROM_MID", "AUTO_CANCEL_SELL_BPS_FROM_MID",
        "AUTO_CANCEL_MAX_PER_CYCLE", "AUTO_CANCEL_STRATEGY",
        "RESERVE_RELIEF_ENABLED", "RESERVE_RELIEF_BUY_CAP", "RESERVE_RELIEF_SELL_CAP",
        "RESERVE_RELIEF_MAX_PER_CYCLE", "RESERVE_RELIEF_GRACE_BPS", "RESERVE_RELIEF_STRATEGY",
        "PENDING_TTL_SEC", "BUY_THROTTLE_SEC", "SELL_THROTTLE_SEC",
        "PRICE_FETCH_RETRIES", "ENV_RELOAD_EVERY_SEC",
        "WIZARD_ENV_PATH"
    }
    env = {k: (os.environ.get(k) or "").strip() for k in allowed}
    return dict_with_defaults(env)

# =========================
# UI
# =========================
class UI:
    HINTS = {
        "MAX_OPEN_BUYS": "0", "MAX_OPEN_SELLS": "0",
        "BUY_OFFSET_BPS": "6", "SELL_OFFSET_BPS": "6",
        "STEP_PCT": "0.5", "BUY_TRANCHE_RLUSD": "10", "SELL_TRANCHE_RLUSD": "10",
        "MIN_NOTIONAL_RLUSD": "10", "SAFETY_BUFFER_XRP": "60",
        "GLOBAL_SL_RLUSD": "0", "SL_DISCOUNT_BPS": "10",
        "INTERVAL": "60", "LEVELS": "3",
        "AUTO_CANCEL_ENABLED": "1",
        "AUTO_CANCEL_BUY_BPS_FROM_MID": "150", "AUTO_CANCEL_SELL_BPS_FROM_MID": "150",
        "AUTO_CANCEL_MAX_PER_CYCLE": "1", "AUTO_CANCEL_STRATEGY": "farthest",
        "RESERVE_RELIEF_ENABLED": "0",
        "RESERVE_RELIEF_BUY_CAP": "10", "RESERVE_RELIEF_SELL_CAP": "2",
        "RESERVE_RELIEF_MAX_PER_CYCLE": "3", "RESERVE_RELIEF_GRACE_BPS": "8",
        "RESERVE_RELIEF_STRATEGY": "farthest",
        "PENDING_TTL_SEC": "120", "BUY_THROTTLE_SEC": "10", "SELL_THROTTLE_SEC": "10",
        "PRICE_FETCH_RETRIES": "3", "ENV_RELOAD_EVERY_SEC": "30",
        "RLUSD_ISSUER": "rMxCKbEDwqr76QuheSUMdEGf4B9xJ8m5De",
        "XRPL_RPC_PRIMARY": "https://s1.ripple.com:51234",
        "XRPL_RPC_FALLBACK": "https://s2.ripple.com:51234",
        "KEY_ALGO": "secp256k1",
    }

    def __init__(self, stop_event: Event):
        self.root = tk.Tk()
        self.root.title("The Grid Wizard v2")
        self.root.configure(bg="black")
        self.stop_event = stop_event

        screen_width = self.root.winfo_screenwidth()
        window_width = int(screen_width * 0.8)
        window_height = 640
        self.root.geometry(f"{window_width}x{window_height}")

        self.env_path = ENV_PATH
        self.clients = connect_clients()

        try:
            self.wallet = load_wallet_from_env()
        except Exception:
            self.wallet = None

        self.issuer = os.environ.get("RLUSD_ISSUER", "rMxCKbEDwqr76QuheSUMdEGf4B9xJ8m5De")
        self.tag = "WIZARD"

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TFrame", background="black")
        style.configure("TLabel", background="black", foreground="white")
        style.configure("TEntry", fieldbackground="black", foreground="white", insertcolor="white")
        style.map("TEntry", background=[('focus', 'black')], foreground=[('focus', 'white')])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        grid_tab = ttk.Frame(self.notebook)
        self.notebook.add(grid_tab, text="Grid Control")

        paned = ttk.PanedWindow(grid_tab, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Log
        log_frame = ttk.Frame(paned)
        paned.add(log_frame, weight=3)
        self.log = scrolledtext.ScrolledText(log_frame, bg="black", fg="white", font=("Courier", 10), height=10)
        self.log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Lower split
        lower_frame = ttk.Frame(paned)
        paned.add(lower_frame, weight=1)
        lower_paned = ttk.PanedWindow(lower_frame, orient=tk.HORIZONTAL)
        lower_paned.pack(fill=tk.BOTH, expand=True)

        # Settings
        settings_outer = ttk.Frame(lower_paned)
        lower_paned.add(settings_outer, weight=3)
        self.settings_canvas = tk.Canvas(settings_outer, bg="black", highlightthickness=0)
        scrollbar = ttk.Scrollbar(settings_outer, orient="vertical", command=self.settings_canvas.yview)
        self.settings_frame = ttk.Frame(self.settings_canvas)
        self.settings_frame.bind("<Configure>", lambda e: self.settings_canvas.configure(scrollregion=self.settings_canvas.bbox("all")))
        self.settings_canvas.create_window((0, 0), window=self.settings_frame, anchor="nw")
        self.settings_canvas.configure(yscrollcommand=scrollbar.set)
        self.settings_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.entries = {}

        wallet_labels = ["CLASSIC_ADDRESS", "PRIVATE_KEY_HEX", "KEY_ALGO"]
        base_labels = [
            "MAX_OPEN_BUYS", "MAX_OPEN_SELLS", "BUY_OFFSET_BPS", "SELL_OFFSET_BPS",
            "STEP_PCT", "BUY_TRANCHE_RLUSD", "SELL_TRANCHE_RLUSD", "GLOBAL_SL_RLUSD",
            "SL_DISCOUNT_BPS", "INTERVAL", "LEVELS",
            "AUTO_CANCEL_BUY_BPS_FROM_MID", "AUTO_CANCEL_SELL_BPS_FROM_MID",
            "AUTO_CANCEL_MAX_PER_CYCLE", "AUTO_CANCEL_STRATEGY", "AUTO_CANCEL_ENABLED",
            "RESERVE_RELIEF_ENABLED", "RESERVE_RELIEF_BUY_CAP", "RESERVE_RELIEF_SELL_CAP",
            "RESERVE_RELIEF_MAX_PER_CYCLE", "RESERVE_RELIEF_GRACE_BPS", "RESERVE_RELIEF_STRATEGY",
            "PENDING_TTL_SEC", "SAFETY_BUFFER_XRP", "MIN_NOTIONAL_RLUSD",
            "RLUSD_ISSUER", "XRPL_RPC_PRIMARY", "XRPL_RPC_FALLBACK", "PRICE_FETCH_RETRIES",
            "ENV_RELOAD_EVERY_SEC"
        ]
        labels = wallet_labels + base_labels

        for i, lbl in enumerate(labels):
            hint = self.HINTS.get(lbl)
            label_text = f"{lbl}" + (f"  (default: {hint})" if hint is not None else "")
            ttk.Label(self.settings_frame, text=label_text).grid(row=i, column=0, padx=5, pady=3, sticky="e")
            width = 42 if lbl == "PRIVATE_KEY_HEX" else 26
            e = ttk.Entry(self.settings_frame, width=width)
            e.grid(row=i, column=1, padx=5, pady=3, sticky="w")
            self.entries[lbl] = e

        btn_row = len(labels)
        save_button = ttk.Button(self.settings_frame, text="Save Settings", command=self.save)
        save_button.grid(row=btn_row, column=0, padx=10, pady=10, sticky="ew")

        def open_config_folder():
            folder = os.path.dirname(self.env_path)
            if os.name == "nt":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])

        open_btn = ttk.Button(self.settings_frame, text="Open Config Folder", command=open_config_folder)
        open_btn.grid(row=btn_row, column=1, padx=10, pady=10, sticky="w")

        # Balances panel
        balance_frame = ttk.Frame(lower_paned)
        lower_paned.add(balance_frame, weight=1)
        self.xrp_grand_total_label = ttk.Label(balance_frame, text="XRP Grand Total: Calculating...")
        self.xrp_grand_total_label.pack(pady=5)
        self.total_xrp_label = ttk.Label(balance_frame, text="Total XRP: Calculating...")
        self.total_xrp_label.pack(pady=5)
        self.xrp_reserve_label = ttk.Label(balance_frame, text="Reserved XRP: Calculating...")
        self.xrp_reserve_label.pack(pady=5)
        self.spendable_xrp_label = ttk.Label(balance_frame, text="Spendable XRP: Calculating...")
        self.spendable_xrp_label.pack(pady=5)
        self.rlusd_balance_label = ttk.Label(balance_frame, text="RLUSD Balance: Calculating...")
        self.rlusd_balance_label.pack(pady=5)

        # Manual Purchase tab
        manual_tab = ttk.Frame(self.notebook)
        self.notebook.add(manual_tab, text="Manual Purchase")
        ttk.Label(manual_tab, text="Buy Currency:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.buy_currency = ttk.Combobox(manual_tab, values=["RLUSD", "XRP"], width=20)
        self.buy_currency.grid(row=0, column=1, padx=5, pady=5); self.buy_currency.set("RLUSD")

        ttk.Label(manual_tab, text="Amount:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = ttk.Entry(manual_tab, width=20); self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(manual_tab, text="Slippage Tolerance (%):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.slip_entry = ttk.Entry(manual_tab, width=20); self.slip_entry.grid(row=2, column=1, padx=5, pady=5)
        self.slip_entry.insert(0, "1")

        purchase_button = ttk.Button(manual_tab, text="Execute Purchase", command=self.execute_purchase)
        purchase_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.root.update()
        self.log_msg(f"[UI] Initialized | Config: {self.env_path}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        if not os.environ.get("CLASSIC_ADDRESS") or not os.environ.get("PRIVATE_KEY_HEX"):
            self.log_msg("[Setup] Enter CLASSIC_ADDRESS and PRIVATE_KEY_HEX, then click Save.")

    def log_msg(self, msg: str):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    def load_settings(self, env: dict):
        # Pre-fill entries: env value if set, else hint/default
        for k, e in self.entries.items():
            e.delete(0, tk.END)
            v = env.get(k, "")
            if (v is None) or (str(v).strip() == ""):
                v = self.HINTS.get(k, "")
            e.insert(0, str(v))

    def update_balances(self, bal_xrp, reserved_xrp, spendable_xrp, rlusd_bal, total_xrp_equiv):
        self.xrp_grand_total_label.config(text=f"XRP Grand Total: {total_xrp_equiv:.6f}")
        self.total_xrp_label.config(text=f"Total XRP: {bal_xrp:.6f}")
        self.xrp_reserve_label.config(text=f"Reserved XRP: {reserved_xrp:.6f}")
        self.spendable_xrp_label.config(text=f"Spendable XRP: {spendable_xrp:.6f}")
        self.rlusd_balance_label.config(text=f"RLUSD Balance: {rlusd_bal:.6f}")

    def save(self):
        # Write a complete .env: any blank gets default (except wallet keys)
        env_now = load_env()  # get current (with defaults)
        for k, e in self.entries.items():
            val = (e.get() or "").strip()
            if k in ("CLASSIC_ADDRESS", "PRIVATE_KEY_HEX"):
                env_now[k] = val  # can remain blank until user fills
            else:
                env_now[k] = val if val != "" else str(self.HINTS.get(k, env_now.get(k, "")))

        # Ensure path key matches file we’re writing
        env_now["WIZARD_ENV_PATH"] = self.env_path

        # Serialize
        lines = ["# Grid Wizard v2 configuration\n\n"]
        for k in sorted(env_now.keys()):
            lines.append(f"{k}={env_now[k]}\n")
        with open(self.env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        load_dotenv(dotenv_path=self.env_path, override=True)
        try:
            self.wallet = load_wallet_from_env()
        except Exception:
            self.wallet = None
        self.log_msg(f"[UI] Settings saved → {self.env_path}")

    def execute_purchase(self):
        try:
            client = healthy_client(self.clients)
            currency = self.buy_currency.get()
            amount = safe_dec(self.amount_entry.get(), "0")
            slip = safe_dec(self.slip_entry.get(), "1") / D(100)
            if amount <= 0:
                self.log_msg("[Purchase] Enter a positive amount.")
                return
            if self.wallet is None:
                self.log_msg("[Purchase] Wallet not configured yet.")
                return
            if currency == "RLUSD":
                from wizard_rlusd_grid_v2 import market_buy_rlusd
                market_buy_rlusd(client, self.wallet, amount, slip, self.issuer, self.tag, self.log_msg)
            elif currency == "XRP":
                from wizard_rlusd_grid_v2 import market_buy_xrp
                market_buy_xrp(client, self.wallet, amount, slip, self.issuer, self.tag, self.log_msg)
            self.log_msg(f"[Purchase] Executed {amount} {currency} with {(slip*100):.2f}% slip tolerance")
        except Exception as e:
            self.log_msg(f"[Purchase] Error: {str(e)}")

    def on_close(self):
        self.stop_event.set()
        self.root.destroy()

# =========================
# Runner loop
# =========================
def run_loop(args, stop_event: Event, ui: Optional[UI] = None):
    def log(msg: str):
        print(msg)
        if ui:
            ui.log_msg(msg)

    env = load_env()
    clients = connect_clients()

    last_reload = 0
    while not stop_event.is_set():
        now = time.time()
        reload_every = safe_int(env.get("ENV_RELOAD_EVERY_SEC"), 30)

        # Only push UI reloads after wallet is configured (prevents clearing inputs during setup)
        classic = env.get("CLASSIC_ADDRESS", "")
        priv = env.get("PRIVATE_KEY_HEX", "")

        if now - last_reload >= reload_every:
            env = load_env()
            last_reload = now
            # Avoid wiping UI fields during setup
            if ui and env.get("CLASSIC_ADDRESS") and env.get("PRIVATE_KEY_HEX"):
                ui.load_settings(env)

        # Early guard: wallet may be blank on first boot
        if not classic or not priv:
            log("[Setup] Waiting for wallet setup. Enter CLASSIC_ADDRESS and PRIVATE_KEY_HEX in the UI, then click Save.")
            # Gentle pacing so user can paste + save without the UI resetting
            time.sleep(30)
            continue

        issuer = env.get("RLUSD_ISSUER")
        safety_buffer_xrp = safe_dec(env.get("SAFETY_BUFFER_XRP"), "60")
        client = healthy_client(clients)

        # Balances pane
        try:
            bal_xrp = get_balance_xrp(client, classic)
            rlusd_bal = get_iou_balance(client, classic, issuer)
            base, owner = get_reserves_xrp(client)
            num_objs = get_account_objects_count(client, classic)
            reserved_xrp = base + owner * D(num_objs) + safety_buffer_xrp
            spendable_xrp = max(D(0), bal_xrp - reserved_xrp)
            px = fetch_orderbook_prices(client, issuer, safe_int(env.get("PRICE_FETCH_RETRIES"), 3))
            mid = px["mid"]
            rlusd_in_xrp = rlusd_bal / mid if mid and mid > 0 else D(0)
            total_xrp_equiv = bal_xrp + rlusd_in_xrp
            if ui:
                ui.update_balances(bal_xrp, reserved_xrp, spendable_xrp, rlusd_bal, total_xrp_equiv)
        except Exception as e:
            log(f"[Error] Failed to fetch balances: {str(e)}")
            time.sleep(10)
            continue

        # Main grid pass (all inputs parsed safely)
        try:
            res = manage_grid_once(
                client=client,
                wallet=load_wallet_from_env(),
                issuer=issuer,
                tag="WIZARD",
                levels=safe_int(env.get("LEVELS"), 3),
                step_pct=safe_dec(env.get("STEP_PCT"), "0.5") / D(100),
                buy_offset_bps=safe_dec(env.get("BUY_OFFSET_BPS"), "6"),
                sell_offset_bps=safe_dec(env.get("SELL_OFFSET_BPS"), "6"),
                buy_tranche_rlusd=safe_dec(env.get("BUY_TRANCHE_RLUSD"), "10"),
                sell_tranche_rlusd=safe_dec(env.get("SELL_TRANCHE_RLUSD"), "10"),
                min_notional=safe_dec(env.get("MIN_NOTIONAL_RLUSD"), "10"),  # fixed name
                safety_buffer_xrp=safety_buffer_xrp,
                max_open_buys=safe_int(env.get("MAX_OPEN_BUYS"), 0),         # safe default
                max_open_sells=safe_int(env.get("MAX_OPEN_SELLS"), 0),       # safe default
                global_sl_rlusd=safe_dec(env.get("GLOBAL_SL_RLUSD"), "0"),
                sl_discount_bps=safe_dec(env.get("SL_DISCOUNT_BPS"), "10"),
                auto_cancel_enabled=(env.get("AUTO_CANCEL_ENABLED") or "1") == "1",
                auto_cancel_buy_bps=safe_dec(env.get("AUTO_CANCEL_BUY_BPS_FROM_MID"), "150"),
                auto_cancel_sell_bps=safe_dec(env.get("AUTO_CANCEL_SELL_BPS_FROM_MID"), "150"),
                auto_cancel_max_per_cycle=safe_int(env.get("AUTO_CANCEL_MAX_PER_CYCLE"), 1),
                auto_cancel_strategy=(env.get("AUTO_CANCEL_STRATEGY") or "farthest"),
                log=log
            )
        except Exception as e:
            log(f"[Error] Grid cycle failed: {str(e)}")
            time.sleep(10)
            continue

        if res:
            mid = res.get("mid")
            orders = []
            existing = res.get("existing_offers", [])
            for of in existing:
                side = _offer_side(of)
                price = _price_vs_xrp(of)
                if price is None:
                    continue
                if side == "buy":
                    xrp_amt = D(drops_to_xrp(of.get("TakerPays", of.get("taker_pays", "0"))))
                    orders.append(f"BUY seq={of['seq']}, {xrp_amt:.6f} XRP @ {price:.6f} RLUSD")
                elif side == "sell":
                    xrp_amt = D(drops_to_xrp(of.get("TakerGets", of.get("taker_gets", "0"))))
                    orders.append(f"SELL seq={of['seq']}, {xrp_amt:.6f} XRP @ {price:.6f} RLUSD")

            balances = {"spendable_xrp": spendable_xrp, "rlusd": rlusd_bal, "total_xrp_equiv": total_xrp_equiv}
            cycle_stats = {
                "placed": res.get("placed", 0),
                "skipped": res.get("skipped", 0),
                "throttle_skips": res.get("throttle_skips", 0),
                "pending_skips": res.get("pending_skips", 0),
                "cancelled": res.get("cancelled", 0),
                "pending_buy": res.get("pending_buy", 0),
                "pending_sell": res.get("pending_sell", 0),
            }
            try:
                log_balances_and_stats(classic, balances, orders, cycle_stats, log)
            except Exception as e:
                log(f"[Error] Logging failed: {str(e)}")

            log(f"[Cycle] mid={mid} placed={cycle_stats['placed']} skipped={cycle_stats['skipped']} "
                f"(throttle={cycle_stats['throttle_skips']} pending={cycle_stats['pending_skips']}) "
                f"cancelled={cycle_stats['cancelled']}")

            log(f"[Balances] Spendable XRP: {spendable_xrp:.6f} | RLUSD: {rlusd_bal:.6f} | "
                f"Total XRP equiv: {total_xrp_equiv:.6f} (Reserved XRP: {reserved_xrp:.6f})")

        interval = safe_int(env.get("INTERVAL"), 60)
        time.sleep(interval)

def _offer_side(of: dict) -> str:
    g = of.get("taker_gets", of.get("TakerGets", {}))
    p = of.get("taker_pays", of.get("TakerPays", {}))
    if isinstance(g, dict) and isinstance(p, (str, int)):
        return "buy"
    if isinstance(g, (str, int)) and isinstance(p, dict):
        return "sell"
    return "other"

def _price_vs_xrp(of: dict) -> Optional[D]:
    g = of.get("taker_gets", of.get("TakerGets", {}))
    p = of.get("taker_pays", of.get("TakerPays", {}))
    try:
        if isinstance(g, dict) and isinstance(p, (str, int)):
            xrp_amt = D(drops_to_xrp(p)); iou_val = D(g.get("value", "0"))
            return iou_val / xrp_amt if xrp_amt > 0 else None
        if isinstance(g, (str, int)) and isinstance(p, dict):
            xrp_amt = D(drops_to_xrp(g)); iou_val = D(p.get("value", "0"))
            return iou_val / xrp_amt if xrp_amt > 0 else None
    except Exception:
        return None
    return None

# =========================
# CLI
# =========================
def main():
    p = argparse.ArgumentParser(description="The Grid Wizard v2 – Grid Trader")
    p.add_argument("--levels", type=int, default=3)
    p.add_argument("--step", type=float, default=0.3)
    p.add_argument("--buy-offset-bps", type=float, default=0.1)
    p.add_argument("--sell-offset-bps", type=float, default=0.15)
    p.add_argument("--interval", type=int, default=60)
    p.add_argument("--ui", action="store_true", help="Launch the Tk UI")
    p.add_argument("--cli", action="store_true", help="Run headless in console")
    args = p.parse_args()

    if not args.ui and not args.cli:
        args.ui = True

    stop_event = Event()
    if args.ui:
        ui = UI(stop_event)
        ui.load_settings(load_env())
        Thread(target=run_loop, args=(args, stop_event, ui), daemon=True).start()
        ui.root.mainloop()
    else:
        run_loop(args, stop_event)

if __name__ == "__main__":
    main()
