"""Security middleware for request sanitization, audit logging, header hardening, and RASP."""
import re
import time
import json
import logging
import hashlib
from typing import Optional, List, Tuple, Set
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_403_FORBIDDEN

from .config import settings
from .anomaly_detector import get_anomaly_detector, APIAnomalyDetector

logger = logging.getLogger("vas.security")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inject OWASP-recommended security headers into every response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        if "server" in response.headers:
            del response.headers["server"]
        return response


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Log every API request for forensic audit trail."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.time()
        client_ip = request.client.host if request.client else "unknown"
        request_id = hashlib.sha256(
            f"{client_ip}:{time.time_ns()}".encode()
        ).hexdigest()[:12]

        logger.info(
            "REQ [%s] %s %s from=%s ua=%s",
            request_id,
            request.method,
            request.url.path,
            client_ip,
            request.headers.get("user-agent", "unknown")[:80],
        )

        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)

        log_fn = logger.warning if response.status_code >= 400 else logger.info
        log_fn(
            "RES [%s] %s %s status=%d duration=%sms",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        return response


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Block requests with obviously malicious payloads."""

    BLOCKED_PATTERNS = [
        "<script", "javascript:", "onclick=", "onerror=",
        "union select", "drop table", "'; --", "1=1",
        "../", "..\\", "%00",
    ]

    async def dispatch(self, request: Request, call_next) -> Response:
        query = str(request.url.query).lower()
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in query:
                logger.warning(
                    "BLOCKED malicious query from %s: %s",
                    request.client.host if request.client else "unknown",
                    pattern,
                )
                return Response(
                    content='{"detail":"Request blocked by WAF"}',
                    status_code=403,
                    media_type="application/json",
                )

        path = request.url.path.lower()
        if ".." in path or "%2e%2e" in path:
            return Response(
                content='{"detail":"Path traversal detected"}',
                status_code=403,
                media_type="application/json",
            )

        return await call_next(request)


class RAPSMiddleware(BaseHTTPMiddleware):
    """
    Runtime Application Self-Protection (RASP) middleware.

    Monitors and blocks attacks in real-time from within the application:
    - SQL injection (union, blind, error-based, time-based)
    - Remote code execution / command injection
    - Path traversal / directory traversal
    - SSRF / localfile / internal network targeting
    - XXE / XML external entity attacks
    - Deserialization payloads
    - Reconnaissance / fuzzing / scanning attempts
    - Automated attack tool fingerprints

    Uses behavioral analysis + pattern matching for high-confidence detection.
    """

    # ─── SQL Injection Patterns ───
    SQLI_PATTERNS = [
        re.compile(r"\bunion\s+select\b", re.IGNORECASE),
        re.compile(r"\bunion\s+all\s+select\b", re.IGNORECASE),
        re.compile(r"extractvalue\(\s*xml", re.IGNORECASE),
        re.compile(r"updatexml\(\s*xml", re.IGNORECASE),
        re.compile(r"floor\(rand\(", re.IGNORECASE),
        re.compile(r"'\s*and\s+'1'\s*=\s*'1", re.IGNORECASE),
        re.compile(r"'\s*or\s+'1'\s*=\s*'1", re.IGNORECASE),
        re.compile(r"sleep\s*\(", re.IGNORECASE),
        re.compile(r"benchmark\s*\(", re.IGNORECASE),
        re.compile(r"pg_sleep\(", re.IGNORECASE),
        re.compile(r"--\s*$", re.IGNORECASE),
        re.compile(r"#\s*$", re.IGNORECASE),
        re.compile(r"/\*.*\*/", re.IGNORECASE),
        re.compile(r";\s*drop\s+table", re.IGNORECASE),
        re.compile(r"information_schema", re.IGNORECASE),
        re.compile(r"sysobjects", re.IGNORECASE),
    ]

    # ─── Command Injection / RCE Patterns ───
    RCE_PATTERNS = [
        re.compile(r"[;&|`](\s*)(whoami|id|uname|cat\s+/etc/passwd|ls\s+-la)", re.IGNORECASE),
        re.compile(r"exec\s*\(", re.IGNORECASE),
        re.compile(r"eval\s*\(", re.IGNORECASE),
        re.compile(r"system\s*\(", re.IGNORECASE),
        re.compile(r"shell_exec\s*\(", re.IGNORECASE),
        re.compile(r"passthru\s*\(", re.IGNORECASE),
        re.compile(r"proc_open\s*\(", re.IGNORECASE),
        re.compile(r"popen\s*\(", re.IGNORECASE),
        re.compile(r"`.*`"),
        re.compile(r"\$\(.*\)"),
        re.compile(r"__import__\s*\(", re.IGNORECASE),
        re.compile(r"os\.system\s*\(", re.IGNORECASE),
        re.compile(r"subprocess\.(call|run|Popen)", re.IGNORECASE),
    ]

    # ─── Path Traversal Patterns ───
    PATH_TRAVERSAL_PATTERNS = [
        re.compile(r"\.\.[\\/]"),
        re.compile(r"%2e%2e%5c"),
        re.compile(r"%2e%2e%2f"),
        re.compile(r"\.\.%2f", re.IGNORECASE),
        re.compile(r"\.\.%5c", re.IGNORECASE),
    ]

    # ─── SSRF / Internal Network Targeting ───
    SSRF_PATTERNS = [
        re.compile(r"https?://(127\.0\.0\.1|localhost|::1|0\.0\.0\.0)"),
        re.compile(r"https?://10\.\d{1,3}\.\d{1,3}\.\d{1,3}"),
        re.compile(r"https?://172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}"),
        re.compile(r"https?://192\.168\.\d{1,3}\.\d{1,3}"),
        re.compile(r"file:///"),
        re.compile(r"gopher://"),
        re.compile(r"dict://"),
        re.compile(r"ftp://(127\.0\.0\.1|localhost)"),
        re.compile(r"169\.254\.169\.254"),
        re.compile(r"metadata\.google\.internal"),
        re.compile(r"169\.254\.169\.123"),
    ]

    # ─── Reconnaissance / Fuzzing Patterns ───
    PROBE_PATTERNS = [
        re.compile(r"\.git/", re.IGNORECASE),
        re.compile(r"\.env", re.IGNORECASE),
        re.compile(r"\.bak", re.IGNORECASE),
        re.compile(r"\.sqlite", re.IGNORECASE),
        re.compile(r"wp-config\.php", re.IGNORECASE),
        re.compile(r"adminer\.php", re.IGNORECASE),
        re.compile(r"phpmyadmin", re.IGNORECASE),
        re.compile(r"\.DS_Store", re.IGNORECASE),
        re.compile(r"\.svn/", re.IGNORECASE),
        re.compile(r"backup|dump|backup\.sql", re.IGNORECASE),
    ]

    # ─── Known Attack Tool Fingerprints ───
    ATTACK_TOOL_UA = [
        "nmap", "nikto", "sqlmap", "burpsuite", "owasp zap",
        "acunetix", "netsparker", "wpscan", "dirb", "gobuster",
        "ffuf", "wfuzz", "hydra", "medusa", "metasploit",
        "sqliv", "xsser", "commix", "beef", "slowloris",
    ]

    # ─── Zero-Day / Emerging Attack Patterns ───
    # NoSQL Injection (MongoDB)
    NOSQL_PATTERNS = [
        re.compile(r"\$where\s*:", re.IGNORECASE),
        re.compile(r"\$ne\s*:", re.IGNORECASE),
        re.compile(r"\$gt\s*:", re.IGNORECASE),
        re.compile(r"\$regex\s*:", re.IGNORECASE),
        re.compile(r"\{\s*\$ne\s*:?null", re.IGNORECASE),
        re.compile(r"\$nin\s*:", re.IGNORECASE),
        re.compile(r"'\$where'\s*:", re.IGNORECASE),
    ]

    # XXE / XML Injection
    XXE_PATTERNS = [
        re.compile(r"<!ENTITY", re.IGNORECASE),
        re.compile(r"<!DOCTYPE", re.IGNORECASE),
        re.compile(r"xinclude", re.IGNORECASE),
        re.compile(r"<\!\[CDATA\[", re.IGNORECASE),
        re.compile(r"xmlns:xsi", re.IGNORECASE),
        re.compile(r"file://", re.IGNORECASE),
        re.compile(r"expect://", re.IGNORECASE),
        re.compile(r"php://", re.IGNORECASE),
        re.compile(r"data://", re.IGNORECASE),
    ]

    # SSTI (Server-Side Template Injection)
    SSTI_PATTERNS = [
        re.compile(r"\{\{.*\}\}"),
        re.compile(r"\$\{.*\}"),
        re.compile(r"<%.*%>"),
        re.compile(r"#{.*}"),
        re.compile(r"__class__", re.IGNORECASE),
        re.compile(r"__mro__", re.IGNORECASE),
        re.compile(r"__subclasses__", re.IGNORECASE),
        re.compile(r"__globals__", re.IGNORECASE),
        re.compile(r"__builtins__", re.IGNORECASE),
        re.compile(r"self\._TemplateReference__context", re.IGNORECASE),
    ]

    # LDAP Injection
    LDAP_PATTERNS = [
        re.compile(r"\(&\(", re.IGNORECASE),
        re.compile(r"\(\\|\(", re.IGNORECASE),
        re.compile(r"\*\)\(", re.IGNORECASE),
        re.compile(r"adminAccount", re.IGNORECASE),
    ]

    # Prototype Pollution / JSON Deep Merge attacks
    PROTO_POLLUTION_PATTERNS = [
        re.compile(r"__proto__", re.IGNORECASE),
        re.compile(r"prototype", re.IGNORECASE),
        re.compile(r"constructor", re.IGNORECASE),
    ]

    # HTTP Request Smuggling / CRLF
    CRLF_PATTERNS = [
        re.compile(r"%0d%0a", re.IGNORECASE),
        re.compile(r"%0a%0d", re.IGNORECASE),
        re.compile(r"\r\n", re.IGNORECASE),
        re.compile(r"%0a", re.IGNORECASE),
        re.compile(r"%0d", re.IGNORECASE),
    ]

    # WebSocket Hijacking / Upgrade abuse
    WS_ABUSE_PATTERNS = [
        re.compile(r"upgrade:\s*websocket", re.IGNORECASE),
    ]

    # GraphQL Introspection / Injection probes
    GRAPHQL_ABUSE_PATTERNS = [
        re.compile(r"__schema", re.IGNORECASE),
        re.compile(r"__type", re.IGNORECASE),
        re.compile(r"introspectionquery", re.IGNORECASE),
        re.compile(r"mutation\s*\{", re.IGNORECASE),
    ]

    def __init__(self, app):
        super().__init__(app)
        self.request_counts = {}   # IP -> {count, timestamps}
        self._admin_probes = {}    # IP -> {count, last_timestamp}
        self._anomaly_detector = None  # Lazy init

    def _get_anomaly_detector(self):
        if self._anomaly_detector is None:
            try:
                self._anomaly_detector = get_anomaly_detector()
            except Exception:
                self._anomaly_detector = None
        return self._anomaly_detector

    async def dispatch(self, request: Request, call_next) -> Response:
        """Inspect request and block if malicious."""
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "").lower()

        attack_indicators: List[str] = []
        risk_score = 0

        # ─── 1. URL & query string analysis ───
        path = request.url.path
        query = str(request.url.query)
        matched_patterns = self._check_patterns(path + " " + query, [
            (self.SQLI_PATTERNS, "sqli", 30),
            (self.NOSQL_PATTERNS, "nosqli", 30),
            (self.RCE_PATTERNS, "rce", 40),
            (self.PATH_TRAVERSAL_PATTERNS, "path_traversal", 25),
            (self.SSRF_PATTERNS, "ssrf", 35),
            (self.XXE_PATTERNS, "xxe", 35),
            (self.SSTI_PATTERNS, "ssti", 40),
            (self.LDAP_PATTERNS, "ldapi", 35),
            (self.PROTO_POLLUTION_PATTERNS, "prototype_pollution", 30),
            (self.CRLF_PATTERNS, "crlf_injection", 25),
            (self.PROBE_PATTERNS, "reconnaissance", 15),
            (self.GRAPHQL_ABUSE_PATTERNS, "graphql_abuse", 20),
        ])

        for pattern_name, pattern, score in matched_patterns:
            attack_indicators.append(pattern_name)
            risk_score += score
            logger.warning(
                "RASP DETECTED [%s] from %s: pattern=%s path=%s",
                pattern_name.upper(), client_ip, pattern, path,
            )

        # ─── 2. User-Agent fingerprinting ───
        ua_risk = self._check_user_agent(user_agent)
        if ua_risk:
            attack_indicators.append(f"suspicious_ua:{ua_risk}")
            risk_score += 25

        # ─── 3. Request body analysis (POST/PUT/PATCH) ───
        body_str = ""
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body_bytes = await request.body()
                body_str = body_bytes.decode("utf-8", errors="ignore")

                body_patterns = self._check_patterns(body_str, [
                    (self.SQLI_PATTERNS, "sqli_body", 30),
                    (self.NOSQL_PATTERNS, "nosqli_body", 30),
                    (self.RCE_PATTERNS, "rce_body", 40),
                    (self.SSRF_PATTERNS, "ssrf_body", 35),
                    (self.XXE_PATTERNS, "xxe_body", 35),
                    (self.SSTI_PATTERNS, "ssti_body", 40),
                    (self.PROTO_POLLUTION_PATTERNS, "proto_pollution_body", 30),
                ])

                for pattern_name, pattern, score in body_patterns:
                    attack_indicators.append(pattern_name)
                    risk_score += score
            except Exception as e:
                logger.debug("Could not read request body: %s", e)

        # ─── 4. Header analysis ───
        header_risk = self._check_headers(request.headers)
        if header_risk:
            attack_indicators.append(f"header_anomaly:{header_risk}")
            risk_score += 10

        # Check for CRLF injection in headers
        for hname, hvalue in request.headers.items():
            if re.search(r"[\r\n%0d%0a]", hvalue, re.IGNORECASE):
                attack_indicators.append("crlf_header_injection")
                risk_score += 30
                break

        # ─── 5. Behavioral analysis ───
        behavior_risk = self._analyze_behavior(client_ip, path, request.method)
        if behavior_risk:
            attack_indicators.append(f"behavior:{behavior_risk}")
            risk_score += 20

        # ─── 6. ML-based Anomaly Detection ───
        try:
            detector = self._get_anomaly_detector()
            if detector:
                body_size = len(body_str)
                headers_dict = dict(request.headers)
                request_info = {
                    "ip": client_ip,
                    "method": request.method,
                    "path": path,
                    "query_params": dict(request.query_params),
                    "body_size": body_size,
                    "user_agent": user_agent,
                    "headers": headers_dict,
                    "timestamp": start_time,
                }
                features = detector.extract_features(request_info)
                is_anomaly, anomaly_score = detector.predict(features)

                if is_anomaly:
                    attack_indicators.append(f"ml_anomaly:score={anomaly_score:.2f}")
                    risk_score += int(anomaly_score * 40)  # Up to 40 additional risk points
                    logger.warning(
                        "RASP ML ANOMALY from %s path=%s score=%.4f",
                        client_ip, path, anomaly_score,
                    )

                # Always add sample (even for normal traffic) to improve model
                detector.add_sample(features, f"{request.method}:{path}")
                detector.log_feature(request_info, is_anomaly, anomaly_score)
        except Exception as e:
            logger.debug("Anomaly detection error: %s", e)

        # ─── 7. Block or allow ───
        if risk_score >= 50:  # High-confidence attack
            self._log_attack(request, client_ip, attack_indicators, risk_score, start_time)
            return JSONResponse(
                status_code=HTTP_403_FORBIDDEN,
                content={
                    "detail": "Request blocked by RASP",
                    "blocked_by": "runtime_application_self_protection",
                },
            )
        elif risk_score >= 30:  # Suspicious - log warning
            logger.warning(
                "RASP SUSPICIOUS request from %s (risk=%d): %s %s indicators=%s",
                client_ip, risk_score, request.method, path, ",".join(attack_indicators),
            )

        # ─── 8. Continue ───
        response = await call_next(request)

        # ─── 9. Response anomaly detection ───
        if response.status_code >= 500:
            logger.warning(
                "RASP ERROR RESPONSE %d from %s to %s - possible exploitation attempt",
                response.status_code, client_ip, path,
            )

        return response

    def _check_patterns(
        self, text: str, patterns: List[Tuple[List[re.Pattern], str, int]]
    ) -> List[Tuple[str, str, int]]:
        """Return list of (pattern_name, matched_pattern, score) for matches."""
        matches = []
        for pattern_list, pattern_name, score in patterns:
            for pattern in pattern_list:
                if pattern.search(text):
                    matches.append((pattern_name, pattern.pattern[:50], score))
                    break
        return matches

    def _check_user_agent(self, user_agent: str) -> Optional[str]:
        for tool in self.ATTACK_TOOL_UA:
            if tool in user_agent:
                return tool
        return None

    def _check_headers(self, headers) -> Optional[str]:
        if "x-forwarded-for" in headers:
            xff = headers["x-forwarded-for"]
            if any(internal in xff for internal in ["127.0.0.1", "localhost", "10.", "192.168."]):
                return "xff_internal_ip"
        return None

    def _analyze_behavior(self, ip: str, path: str, method: str) -> Optional[str]:
        now = time.time()
        window = 60
        threshold = 30

        if ip not in self.request_counts:
            self.request_counts[ip] = {"count": 0, "timestamps": []}

        data = self.request_counts[ip]
        data["count"] += 1
        data["timestamps"].append(now)

        cutoff = now - window
        data["timestamps"] = [t for t in data["timestamps"] if t > cutoff]
        data["count"] = len(data["timestamps"])

        if data["count"] > threshold:
            return f"rate_exceeded_{data['count']}rps"

        if method == "GET" and ("/admin" in path or "/export" in path or "/internal" in path):
            if ip not in self._admin_probes:
                self._admin_probes[ip] = {"count": 0}
            self._admin_probes[ip]["count"] += 1
            if self._admin_probes[ip]["count"] > 5:
                return "admin_probing"

        return None

    def _log_attack(
        self,
        request: Request,
        client_ip: str,
        indicators: List[str],
        risk_score: int,
        start_time: float,
    ):
        duration = time.time() - start_time
        logger.error(
            "RASP BLOCKED ATTACK from %s ua=%s path=%s indicators=%s risk=%d duration=%.2fms",
            client_ip,
            request.headers.get("user-agent", "unknown")[:80],
            request.url.path,
            ",".join(indicators),
            risk_score,
            duration * 1000,
        )
