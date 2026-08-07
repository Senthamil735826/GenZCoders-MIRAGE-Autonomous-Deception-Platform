import logging

logger = logging.getLogger("mirage.response")

def handle_threat(threat_info, db_log_func=None):
    """Decide response action based on threat severity."""

    ip = threat_info["source_ip"]
    severity = threat_info["severity"]
    patterns = threat_info.get("matched_patterns", [])

    action = "MONITOR"
    if severity == "CRITICAL":
        action = "BLOCK_AND_DECEIVE"
    elif severity == "HIGH":
        action = "DECEIVE"

    logger.info(f"[RESPONSE] {action} for {ip} | Severity: {severity}")

    # Log to database
    if db_log_func:
        db_log_func(
            source_ip=ip,
            event_type=action,
            severity=severity,
            details=str(patterns)
        )

    return {
        "action": action,
        "source_ip": ip,
        "severity": severity
    }