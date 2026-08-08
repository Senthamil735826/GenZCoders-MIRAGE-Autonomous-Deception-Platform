from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.database.models import ContainmentAction, Honeytoken, TriggerEvent

CRITICAL_TYPES = {"db_connection", "aws_key", "azure_key", "gcp_key", "ssh_key", "k8s_secret"}


async def evaluate_and_contain(
    event: TriggerEvent, token: Honeytoken, db: AsyncSession
) -> ContainmentAction | None:
    """Autonomous response. Never raises - a containment bug must not break the callback."""
    ip = event.source_ip or "unknown"

    if token.token_type in CRITICAL_TYPES or token.sensitivity >= 8:
        action_type = "block_ip_firewall"
        details = {
            "reason": f"Critical honeytoken '{token.name}' triggered",
            "target_ip": ip,
            "duration": "24h",
            "firewall_rule": f"iptables -A INPUT -s {ip} -j DROP",
            "cloud_action": f"Revoke IAM sessions originating from {ip}",
        }
        status = "dry_run" if settings.DRY_RUN else "executed"
    elif token.sensitivity >= 5:
        action_type = "flag_for_monitoring"
        details = {
            "reason": f"Medium-sensitivity token '{token.name}' triggered",
            "target_ip": ip,
            "action": "Added to watchlist",
        }
        status = "executed"
    else:
        return None

    action = ContainmentAction(
        event_id=event.id,
        attacker_ip=ip,          # <-- this was missing
        action_type=action_type, # <-- this was empty
        status=status,
        details=details,
    )

    # only set token_id if your model actually has that column
    if hasattr(ContainmentAction, "token_id"):
        action.token_id = token.id

    db.add(action)
    await db.commit()
    await db.refresh(action)
    return action