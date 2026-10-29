## 2026-10-29 — PyJWT Migration
**Risk identified:** python-jose is unmaintained and deprecated, creating a security risk for authentication systems.
**Migration target:** PyJWT, which is the standard, actively maintained Python JWT library.
**Migrated this session:** Replaced python-jose with PyJWT in dependencies and core security JWT modules.
**Remaining:** None.
**Next session:** Look for other unmaintained libraries (like python-multipart or passlib which might be lagging).
