"""
Minimal Paystack client.
Docs: https://paystack.com/docs/api/transaction/

We only ever trust a payment as 'Successful' after calling verify_transaction
server-side and checking status == 'success' AND that the amount returned
matches what we expected. Never trust the frontend's word that a payment
succeeded — the frontend redirect/callback is just a hint to go verify.
"""
import httpx
from app.config import get_settings

settings = get_settings()

PAYSTACK_BASE_URL = "https://api.paystack.co"


class PaystackError(Exception):
    pass


def _headers():
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def initialize_transaction(email: str, amount_ghs: float, reference: str, callback_url: str = None) -> dict:
    """
    amount_ghs is in Ghana Cedis (e.g. 1500.50). Paystack expects the amount
    in the smallest currency unit (pesewas), so we multiply by 100.
    """
    payload = {
        "email": email,
        "amount": int(round(amount_ghs * 100)),
        "currency": "GHS",
        "reference": reference,
    }
    if callback_url:
        payload["callback_url"] = callback_url

    with httpx.Client(timeout=15.0) as client:
        response = client.post(f"{PAYSTACK_BASE_URL}/transaction/initialize", json=payload, headers=_headers())

    data = response.json()
    if not data.get("status"):
        raise PaystackError(data.get("message", "Failed to initialize Paystack transaction."))
    return data["data"]  # contains authorization_url, access_code, reference


def verify_transaction(reference: str) -> dict:
    with httpx.Client(timeout=15.0) as client:
        response = client.get(f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}", headers=_headers())

    data = response.json()
    if not data.get("status"):
        raise PaystackError(data.get("message", "Failed to verify Paystack transaction."))
    return data["data"]  # contains status ('success'/'failed'), amount, currency, etc.


def verify_webhook_signature(raw_body: bytes, signature_header: str) -> bool:
    """
    Paystack signs webhook payloads with HMAC-SHA512 using your secret key.
    Always verify this before trusting a webhook — otherwise anyone could
    POST a fake 'payment successful' event to your webhook URL.
    See: https://paystack.com/docs/payments/webhooks/
    """
    import hmac
    import hashlib
    computed = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(), raw_body, hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed, signature_header or "")
