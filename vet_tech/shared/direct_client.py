"""Private, authenticated non-clinical messaging transport."""
from vet_tech.shared.xano_client import XanoRequestError, xano_request


async def direct_request(profile, token, payload):
    if profile not in ("tutor", "veterinario") or not token:
        raise XanoRequestError("Sessão inválida.", 401)
    result = await xano_request("POST", "vettech-support", f"{profile}/conversas",
                                auth_token=token, json_payload={"payload": payload})
    if not isinstance(result, dict) or not any(key in result for key in ("thread", "threads", "tutors", "veterinarians")):
        raise XanoRequestError("Resposta da conversa inválida.")
    return result
