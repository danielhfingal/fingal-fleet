from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
import os
from pyotp import TOTP
from ipaddress import ip_address

API_KEY = os.getenv("FINGAL_API_KEY")
TOTP_SECRET = os.getenv("FINGAL_TOTP_SECRET")
ALLOWED_IPS = [ip.strip() for ip in os.getenv("FINGAL_ALLOWED_IPS", "").split(",") if ip.strip()]
CLIENT_CERT_REQUIRED = os.getenv("FINGAL_MTLS", "false").lower() == "true"

async def nuclear_auth(
    request: Request,
    api_key: str | None = None,
    x_2fa: str | None = None,
):
    if ALLOWED_IPS and request.client.host not in ALLOWED_IPS:
        raise HTTPException(403, "IP not allowed")
    if not API_KEY or api_key != API_KEY:
        raise HTTPException(401, "invalid key")
    if TOTP_SECRET and (not x_2fa or not TOTP(TOTP_SECRET).verify(x_2fa)):
        raise HTTPException(401, "invalid 2fa")
    if CLIENT_CERT_REQUIRED and not request.scope.get("client_cert"):
        raise  raise HTTPException(403, "mTLS required")

Nuclear = Depends(nuclear_auth)