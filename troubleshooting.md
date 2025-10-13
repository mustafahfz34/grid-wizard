🧩 Troubleshooting

### 🪙 License not found
**Message:**
[NFT] License not found. Hold any NFT from issuer rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52 to unlock Pro features.
https://xrp.cafe/usercollection/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52/42000

**Fix:**  
Ensure your connected wallet owns at least one NFT from the issuer above.  
Use the UI or `debug_list_issuers()` helper to confirm what the node returns.


### ⚙️ Trustline missing
**Message:**
[Trustline] RLUSD missing. Creating...


 **Fix:**  
The bot automatically creates the RLUSD trustline. If it fails, check you have enough XRP for reserves.


### 🌐 RPC unavailable
**Message:**  
`License check failed: RPC unavailable`  
**Fix:**  
Switch to a working XRPL endpoint:
XRPL_RPC_PRIMARY=https://s1.ripple.com:51234
XRPL_RPC_FALLBACK=https://s2.ripple.com:51234



### 🕒 Throttle / pending skips
If you see repeated `[OpenCap]` or `pending_skips` > 0, you may be hitting cap limits or throttles.  
Adjust:
MAX_OPEN_BUYS=...
PENDING_TTL_SEC=...
BUY_THROTTLE_SEC=...
