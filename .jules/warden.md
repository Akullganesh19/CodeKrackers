## 2024-05-24 — Active PII Exposure in Logs

**Data traced:** Email addresses and Phone numbers.
**Exposure found:** PII is logged in plaintext across several endpoints, including:
- User creation (e.g., `USER_CREATED email=...`)
- OTP sending (e.g., `OTP sent to ...`, `SECURITY: Generated OTP for ... -> ...`)
- Spam checks (e.g., `SPAM_CHECK phone=... action=... score=...`)
- SMS gateway error logs
- Authentication failures
- Phone lookups (e.g., `PHONE_LOOKUP_CACHED phone=...`)
- OpenClaw Agent logs (SMS messages can contain sensitive context)
These logs are collected through `structlog` in `backend/core/logger.py` and outputted to stdout/json.

**Risk:** Active exposure. Any developer or infrastructure service (e.g., Splunk, Datadog) with access to standard out or file logs can see user emails, phone numbers, and even OTP codes.

**Proposed Fix:** Modify the `structlog` configuration in `backend/core/logger.py` to add a processor that universally redacts PII (Emails, Phone numbers, and 6-digit OTP codes) from `event_dict` fields before they are rendered.

**Coverage confirmed:** TBD (will test by generating logs through endpoints)
**Still exposed elsewhere:** TBD (need to check DB retention paths)
**Fix:** Modified `structlog` configuration in `backend/core/logger.py` to add a universal `redact_pii` processor before rendering. It uses regex to identify Emails, Phone numbers (various formats), and 6-digit OTP codes, and masks them (e.g., `user@example.com` -> `u***@example.com`, `+1 234 567 8900` -> `+* *** *** 8900`, `123456` -> `******`).
**Coverage confirmed:** Verified by running a standalone script passing simulated application log patterns (User creation, Spam checks, OTP generation, Gateway errors) into the logger. All PII and OTP values were masked successfully.
**Refinement:** Modified `recursively_redact` in `backend/core/logger.py` to recursively traverse structs (dicts, lists, tuples) to mask sensitive data inside nested objects, as well as handle scalar types like `int` properly.
