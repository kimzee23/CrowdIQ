"""
CrowdIQ — Keycloak Client
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

class KeycloakClientStub:
    """
    Placeholder for Keycloak integration.
    Currently, the project uses the internal JWT utility in `src.infrastructure.security.jwt`.
    If you choose to switch to Keycloak fully, you would implement the token validation
    and user management sync here.
    """
    def __init__(self, server_url: str, realm_name: str, client_id: str) -> None:
        self.server_url = server_url
        self.realm_name = realm_name
        self.client_id = client_id
        logger.info("Initializing Keycloak client for realm %s", self.realm_name)

    async def verify_token(self, token: str) -> dict:
        # TODO: Implement actual Keycloak token introspection or signature verification
        pass

# keycloak_client = KeycloakClientStub(
#     server_url="http://localhost:8080/auth/",
#     realm_name="crowdiq",
#     client_id="crowdiq-backend"
# )
