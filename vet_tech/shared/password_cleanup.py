"""Limpeza periódica gratuita, executada somente pelo processo Python local."""
import asyncio
from contextlib import asynccontextmanager, suppress
import hashlib
import hmac
import logging
import os
import time

from vet_tech.shared.xano_client import AUTH_API_GROUP, XanoRequestError, xano_request

logger = logging.getLogger(__name__)
CLEANUP_INTERVAL_SECONDS = 3600


async def cleanup_password_records() -> bool:
    secret = os.environ.get("PASSWORD_CODE_SECRET", "")
    if len(secret) < 32:
        return False
    timestamp = int(time.time() * 1000)
    signature = hmac.new(secret.encode(), f"password-cleanup:{timestamp}".encode(), hashlib.sha256).hexdigest()
    try:
        result = await xano_request("POST", AUTH_API_GROUP, "acesso/password-reset/cleanup", json_payload={"timestamp": timestamp, "signature": signature})
    except XanoRequestError:
        # Nunca registrar assinatura, corpo ou credenciais do serviço.
        logger.warning("A limpeza de códigos será tentada no próximo ciclo.")
        return False
    return isinstance(result, dict) and result.get("success") is True


async def _cleanup_loop():
    while True:
        await cleanup_password_records()
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)


@asynccontextmanager
async def password_cleanup_lifespan():
    if len(os.environ.get("PASSWORD_CODE_SECRET", "")) < 32:
        yield
        return
    task = asyncio.create_task(_cleanup_loop())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
