"""
wizard_license.py
Grid Wizard NFT License Verification

Purpose:
- Ensures the user holds at least one NFT from the authorized Grid Wizard issuer.
- No .env dependency — the issuer is hardcoded for transparency and immutability.
- Works on any XRPL network (mainnet recommended).

Usage:
from wizard_license import check_license
ok, reason = check_license(client, classic_address, log)
"""

from xrpl.models.requests import AccountNFTs

# =====================================================================
# Configuration
# =====================================================================

# The official Grid Wizard NFT issuer address (hardcoded)
LICENSE_ISSUERS = [
    "rfYZ17wwhA4Be23fw8zthVmQQnrcdDRi52",  # Grid Wizard Labs (Las Vegas)
]

# Optional: restrict to a specific collection Taxon (set to None to ignore)
LICENSE_TAXON = None  # or 42000 if you later re-enable Taxon filtering

# =====================================================================
# License check
# =====================================================================

def check_license(client, address: str, log=None):
    """
    Checks whether the given XRPL address holds a valid Grid Wizard license NFT.

    Returns:
        (bool, str): (True, success_message) or (False, error_message)
    """
    try:
        req = AccountNFTs(account=address, limit=400)
        resp = client.request(req)
        if not resp.is_successful():
            return False, "[NFT] Failed to query NFTs for license check."

        nfts = resp.result.get("account_nfts", [])
        if not nfts:
            return False, f"[NFT] No NFTs found for account {address}."

        for nft in nfts:
            issuer = nft.get("Issuer")
            taxon = nft.get("NFTokenTaxon")

            if issuer in LICENSE_ISSUERS:
                if LICENSE_TAXON is None or taxon == LICENSE_TAXON:
                    if log:
                        log(f"[NFT] License verified: issuer={issuer}, taxon={taxon}")
                    return True, f"License verified: NFT from {issuer}"
        return (
            False,
            f"[NFT] License not found. Hold any NFT from issuer {LICENSE_ISSUERS[0]} to unlock Pro features.",
        )
    except Exception as e:
        return False, f"[NFT] License check error: {str(e)}"

# =====================================================================
# Self-test
# =====================================================================

if __name__ == "__main__":
    print("This module is intended for import only.")
    print(f"Authorized issuer(s): {LICENSE_ISSUERS}")
