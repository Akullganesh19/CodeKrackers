def test_auth_priv_esc():
    with open("backend/api/auth.py", "r") as f:
        content = f.read()
        assert "role=UserRole(otp_verify.role)" not in content
        assert "role=UserRole(user_in.role)" not in content
        assert "role=UserRole.CITIZEN" in content

    with open("backend/api/v1/endpoints/auth.py", "r") as f:
        content = f.read()
        assert "role=otp_verify.role" not in content
        assert "role=user_in.role" not in content
        assert "role=\"citizen\"" in content
