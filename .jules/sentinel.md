# Sentinel's Journal - Critical Security Learnings

## 2025-05-15 - [Hardcoded Admin Bypass]
**Vulnerability:** Hardcoded `dummy_token` in `decode_token` allowed full admin access without authentication.
**Learning:** Development helpers left in production code are a common source of critical vulnerabilities.
**Prevention:** Use environment-based flags to enable/disable development features and ensure they default to disabled in production.
