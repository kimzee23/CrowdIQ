import pytest
from httpx import AsyncClient


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _register(async_client: AsyncClient, username: str, email: str) -> dict:
    """Register and return the JSON response."""
    resp = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": "Password123!"},
    )
    return resp


async def _verify_and_login(
    async_client: AsyncClient,
    email: str,
    mock_redis_store: dict,
) -> str:
    """Grab OTP from mock store, verify, then login. Returns access_token."""
    otp = mock_redis_store.get(f"otp:{email}")
    assert otp is not None, f"OTP not found for {email}"
    await async_client.post("/api/v1/auth/verify-otp", json={"email": email, "otp": otp})
    login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    return login.json()["access_token"]


# ── Tests ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_returns_message_not_tokens(
    async_client: AsyncClient, mock_redis_store: dict
):
    """Registration should return a message + email, not JWT tokens."""
    resp = await _register(async_client, "ade_ope", "ade@gmail.com")
    assert resp.status_code == 201
    data = resp.json()
    assert "message" in data
    assert "email" in data
    assert "access_token" not in data
    assert "refresh_token" not in data
    # OTP should have been auto-sent to mock Redis
    assert f"otp:ade@gmail.com" in mock_redis_store


@pytest.mark.asyncio
async def test_login_blocked_before_email_verification(
    async_client: AsyncClient, mock_redis_store: dict
):
    """Login must return 401 until the user verifies their email."""
    await _register(async_client, "unverified_user", "unverified@example.com")

    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "unverified@example.com", "password": "Password123!"},
    )
    assert login_resp.status_code == 401
    assert "not verified" in login_resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_succeeds_after_email_verification(
    async_client: AsyncClient, mock_redis_store: dict
):
    """After verifying OTP, login should return JWT tokens."""
    email = "verified@example.com"
    await _register(async_client, "verified_user", email)

    # Verify OTP
    otp = mock_redis_store[f"otp:{email}"]
    verify_resp = await async_client.post(
        "/api/v1/auth/verify-otp", json={"email": email, "otp": otp}
    )
    assert verify_resp.status_code == 200

    # Login should now succeed
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_get_profile(async_client: AsyncClient, mock_redis_store: dict):
    """After verification and login, /me should return the user profile."""
    email = "meuser@example.com"
    await _register(async_client, "meuser", email)
    token = await _verify_and_login(async_client, email, mock_redis_store)

    resp = await async_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == "meuser"
    assert resp.json()["is_verified"] is True


@pytest.mark.asyncio
async def test_otp_send_and_verify_full_flow(
    async_client: AsyncClient, mock_redis_store: dict
):
    """Full OTP flow: register → auto-OTP sent → verify → login."""
    email = "otpuser@example.com"
    await _register(async_client, "otpuser", email)

    # OTP auto-sent on registration
    redis_key = f"otp:{email}"
    assert redis_key in mock_redis_store
    auto_otp = mock_redis_store[redis_key]
    assert len(auto_otp) == 6

    # Verify with wrong OTP → 422
    verify_bad = await async_client.post(
        "/api/v1/auth/verify-otp", json={"email": email, "otp": "000000"}
    )
    assert verify_bad.status_code == 422
    assert "Invalid or expired OTP" in verify_bad.json()["detail"]

    # Verify with correct OTP → 200
    verify_good = await async_client.post(
        "/api/v1/auth/verify-otp", json={"email": email, "otp": auto_otp}
    )
    assert verify_good.status_code == 200
    assert verify_good.json()["message"] == "Email verified successfully"

    # OTP deleted from Redis after successful verification
    assert redis_key not in mock_redis_store

    # Can now log in
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    assert login_resp.status_code == 200

    # Profile shows is_verified = True
    token = login_resp.json()["access_token"]
    me_resp = await async_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.json()["is_verified"] is True


@pytest.mark.asyncio
async def test_resend_otp_works(async_client: AsyncClient, mock_redis_store: dict):
    """User can request a fresh OTP via /send-otp endpoint."""
    email = "resend@example.com"
    await _register(async_client, "resenduser", email)

    # Request a fresh OTP
    send_resp = await async_client.post(
        "/api/v1/auth/send-otp", json={"email": email}
    )
    assert send_resp.status_code == 200
    assert send_resp.json()["message"] == "OTP sent successfully"
    assert f"otp:{email}" in mock_redis_store


@pytest.mark.asyncio
async def test_send_otp_for_nonexistent_email(
    async_client: AsyncClient, mock_redis_store: dict
):
    """Sending OTP to an unknown email should return 404."""
    resp = await async_client.post(
        "/api/v1/auth/send-otp", json={"email": "ghost@nowhere.com"}
    )
    assert resp.status_code == 404


# ── Password Reset Flow Tests ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_forgot_password_sends_reset_otp(
    async_client: AsyncClient, mock_redis_store: dict
):
    """forgot-password should store a reset OTP in Redis and return a generic message."""
    email = "resetme@example.com"
    await _register(async_client, "resetme", email)
    otp = mock_redis_store[f"otp:{email}"]
    await async_client.post("/api/v1/auth/verify-otp", json={"email": email, "otp": otp})

    # Request password reset
    resp = await async_client.post(
        "/api/v1/auth/forgot-password", json={"email": email}
    )
    assert resp.status_code == 200
    assert "reset OTP" in resp.json()["message"]

    # Reset OTP must be in Redis under a separate key
    assert f"reset_otp:{email}" in mock_redis_store
    reset_otp = mock_redis_store[f"reset_otp:{email}"]
    assert len(reset_otp) == 6


@pytest.mark.asyncio
async def test_forgot_password_unknown_email_returns_generic_message(
    async_client: AsyncClient, mock_redis_store: dict
):
    """Should not reveal whether the email is registered (anti-enumeration)."""
    resp = await async_client.post(
        "/api/v1/auth/forgot-password", json={"email": "nobody@nowhere.com"}
    )
    assert resp.status_code == 200
    assert "reset OTP" in resp.json()["message"]
    # No OTP stored because user doesn't exist
    assert "reset_otp:nobody@nowhere.com" not in mock_redis_store


@pytest.mark.asyncio
async def test_verify_reset_otp_with_wrong_otp_is_rejected(
    async_client: AsyncClient, mock_redis_store: dict
):
    """Submitting the wrong reset OTP should return 422."""
    email = "wrongotp@example.com"
    await _register(async_client, "wrongotp", email)
    otp = mock_redis_store[f"otp:{email}"]
    await async_client.post("/api/v1/auth/verify-otp", json={"email": email, "otp": otp})

    await async_client.post("/api/v1/auth/forgot-password", json={"email": email})

    resp = await async_client.post(
        "/api/v1/auth/verify-reset-otp",
        json={"email": email, "otp": "000000"},
    )
    assert resp.status_code == 422
    assert "Invalid or expired reset OTP" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_full_password_reset_flow(
    async_client: AsyncClient, mock_redis_store: dict
):
    """
    Full secure password reset flow:
      1. Register + verify account
      2. forgot-password  → reset OTP sent
      3. verify-reset-otp → reset token issued, OTP consumed (single use)
      4. reset-password   → new password accepted
      5. Login with old password fails
      6. Login with new password succeeds
    """
    email = "fullreset@example.com"
    old_password = "OldPass123!"
    new_password = "NewPass456@"

    # 1. Register and verify
    await async_client.post(
        "/api/v1/auth/register",
        json={"username": "fullreset", "email": email, "password": old_password},
    )
    reg_otp = mock_redis_store[f"otp:{email}"]
    await async_client.post(
        "/api/v1/auth/verify-otp", json={"email": email, "otp": reg_otp}
    )

    # 2. Request password reset
    forgot_resp = await async_client.post(
        "/api/v1/auth/forgot-password", json={"email": email}
    )
    assert forgot_resp.status_code == 200
    reset_otp = mock_redis_store[f"reset_otp:{email}"]

    # 3. Verify reset OTP → get reset token
    verify_resp = await async_client.post(
        "/api/v1/auth/verify-reset-otp",
        json={"email": email, "otp": reset_otp},
    )
    assert verify_resp.status_code == 200
    reset_token = verify_resp.json()["reset_token"]
    assert reset_token

    # OTP must be deleted after single use
    assert f"reset_otp:{email}" not in mock_redis_store

    # Cannot reuse the same OTP
    reuse_resp = await async_client.post(
        "/api/v1/auth/verify-reset-otp",
        json={"email": email, "otp": reset_otp},
    )
    assert reuse_resp.status_code == 422

    # 4. Reset password with the token
    reset_resp = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": new_password},
    )
    assert reset_resp.status_code == 200
    assert reset_resp.json()["message"] == "Password reset successfully"

    # 5. Old password no longer works
    old_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": old_password},
    )
    assert old_login.status_code == 401

    # 6. New password works
    new_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": new_password},
    )
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()

