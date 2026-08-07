import logging

logger = logging.getLogger("mirage.detection")

SUSPICIOUS_PATTERNS = [
    "nmap", "sqlmap", "nikto", "dirb",
    "' OR 1=1", "<script>", "../", "cmd.exe"
]

def analyze_request(source_ip, path, payload=""):
    """Analyze incoming request for threats."""
    threats = []

    for pattern in SUSPICIOUS_PATTERNS:
        if pattern.lower() in path.lower() or pattern.lower() in payload.lower():
            threats.append(pattern)

    if threats:
        severity = "CRITICAL" if len(threats) > 2 else "HIGH"
        logger.warning(f"[DETECT] Threat from {source_ip} | Patterns: {threats}")
        return {
            "is_threat": True,
            "source_ip": source_ip,
            "severity": severity,
            "matched_patterns": threats
        }

    return {"is_threat": False, "source_ip": source_ip}