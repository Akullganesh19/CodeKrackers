## 2024-05-15 — [Python-Jose to PyJWT Migration]
**Risk identified:** `python-jose` is an unmaintained library that hasn't seen an update in years, and its dependency on `cryptography` can cause installation and security vulnerability issues over time. New team members will likely expect modern, maintained alternatives.
**Migration target:** The ecosystem is moving toward `PyJWT` (which is standard and actively maintained) for JSON Web Token processing.
**Migrated this session:** Replaced `python-jose` with `PyJWT` in `requirements.txt` and `requirements_win.txt`, and updated the code in `backend/core/security.py` and `backend/core/deps.py` to use `import jwt` instead of `from jose import jwt`.
**Remaining:** No further migration steps required for this specific dependency.
**Next session:** Look for other legacy dependencies or patterns like SQLAlchemy 1.x style queries if they exist.
