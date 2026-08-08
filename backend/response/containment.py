"""
MIRAGE Containment Engine

Handles autonomous defensive responses for detected threats.

Current actions are SAFE/SIMULATED for the hackathon demo.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ============================================================
# Utility
# ============================================================

def utc_now() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# Containment Engine
# ============================================================

class ContainmentEngine:

    def __init__(self, db=None):
        self.db = db
        self.actions_taken: List[Dict[str, Any]] = []

    # --------------------------------------------------------
    # Threat Evaluation
    # --------------------------------------------------------

    def evaluate_threat(
        self,
        threat_event: Dict[str, Any],
    ) -> Optional[List[Dict[str, Any]]]:

        severity = str(
            threat_event.get(
                "severity",
                "info",
            )
        ).lower()

        if severity == "critical":
            return self.full_containment(
                threat_event
            )

        elif severity == "high":
            return self.partial_containment(
                threat_event
            )

        elif severity == "medium":
            return self.monitor_only(
                threat_event
            )

        return None

    # --------------------------------------------------------
    # Critical Threat
    # --------------------------------------------------------

    def full_containment(
        self,
        threat_event: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        source_ip = threat_event.get(
            "source_ip",
            "unknown",
        )

        actions = []

        actions.append(
            self.block_ip_firewall(
                source_ip
            )
        )

        actions.append(
            self.isolate_session(
                source_ip
            )
        )

        actions.append(
            self.revoke_credentials(
                source_ip
            )
        )

        actions.append(
            self.alert_security_team(
                threat_event
            )
        )

        actions.append(
            self.snapshot_forensics(
                source_ip
            )
        )

        return actions

    # --------------------------------------------------------
    # High Threat
    # --------------------------------------------------------

    def partial_containment(
        self,
        threat_event: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        source_ip = threat_event.get(
            "source_ip",
            "unknown",
        )

        actions = []

        actions.append(
            self.rate_limit_ip(
                source_ip
            )
        )

        actions.append(
            self.alert_security_team(
                threat_event
            )
        )

        return actions

    # --------------------------------------------------------
    # Medium Threat
    # --------------------------------------------------------

    def monitor_only(
        self,
        threat_event: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        return [
            self.alert_security_team(
                threat_event
            )
        ]

    # --------------------------------------------------------
    # Block IP
    # --------------------------------------------------------

    def block_ip_firewall(
        self,
        ip_address: str,
    ) -> Dict[str, Any]:

        action = {
            "action": "block_ip",
            "target": ip_address,
            "method": "firewall",
            "timestamp": utc_now(),
            "status": "simulated",
        }

        self.actions_taken.append(action)

        return action

    # --------------------------------------------------------
    # Isolate Session
    # --------------------------------------------------------

    def isolate_session(
        self,
        ip_address: str,
    ) -> Dict[str, Any]:

        action = {
            "action": "isolate_session",
            "target": ip_address,
            "method": "session_isolation",
            "timestamp": utc_now(),
            "status": "simulated",
        }

        self.actions_taken.append(action)

        return action

    # --------------------------------------------------------
    # Revoke Credentials
    # --------------------------------------------------------

    def revoke_credentials(
        self,
        identifier: str,
    ) -> Dict[str, Any]:

        action = {
            "action": "revoke_credentials",
            "target": identifier,
            "timestamp": utc_now(),
            "status": "simulated",
        }

        self.actions_taken.append(action)

        return action

    # --------------------------------------------------------
    # Alert Security Team
    # --------------------------------------------------------

    def alert_security_team(
        self,
        threat_event: Dict[str, Any],
    ) -> Dict[str, Any]:

        action = {
            "action": "alert_sent",
            "channels": [
                "email",
                "siem",
                "slack",
            ],
            "event": threat_event,
            "timestamp": utc_now(),
            "status": "simulated",
        }

        self.actions_taken.append(action)

        return action

    # --------------------------------------------------------
    # Rate Limit IP
    # --------------------------------------------------------

    def rate_limit_ip(
        self,
        ip_address: str,
    ) -> Dict[str, Any]:

        action = {
            "action": "rate_limit",
            "target": ip_address,
            "limit": "10 requests/minute",
            "timestamp": utc_now(),
            "status": "simulated",
        }

        self.actions_taken.append(action)

        return action

    # --------------------------------------------------------
    # Forensic Snapshot
    # --------------------------------------------------------

    def snapshot_forensics(
        self,
        ip_address: str,
    ) -> Dict[str, Any]:

        action = {
            "action": "forensic_snapshot",
            "target": ip_address,
            "data_collected": [
                "network_logs",
                "process_list",
                "memory_dump",
            ],
            "timestamp": utc_now(),
            "status": "simulated",
        }

        self.actions_taken.append(action)

        return action

    # --------------------------------------------------------
    # Get Action History
    # --------------------------------------------------------

    def get_actions(
        self,
    ) -> List[Dict[str, Any]]:

        return self.actions_taken


# ============================================================
# Network Controller
# ============================================================

class NetworkController:

    async def isolate_attacker(
        self,
        ip: str,
    ) -> Dict[str, Any]:

        safe_id = (
            ip.replace(".", "_")
            .replace(":", "_")
        )

        print(
            f"[CONTAINMENT] Isolating {ip}"
        )

        return {
            "id": f"iso_{safe_id}",
            "target": ip,
            "status": "isolated",
            "timestamp": utc_now(),
        }


# ============================================================
# Global Instances
# ============================================================

containment_engine = ContainmentEngine()

network_controller = NetworkController()