from backend.core.security import verify_password, get_password_hash, create_access_token, decode_token
pwd = "SecurePassword1!"
hsh = get_password_hash(pwd)
assert verify_password(pwd, hsh)
assert not verify_password("wrong", hsh)
token = create_access_token("test_user")
decoded = decode_token(token)
assert decoded["sub"] == "test_user"
print("All good!")
