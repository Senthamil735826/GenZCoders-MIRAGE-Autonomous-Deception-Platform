import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Interaction


# ============================================================
# Logging Setup
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_FILE = LOG_DIR / "deception.log"

logger = logging.getLogger("mirage.detection")

if not logger.handlers:
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


# ============================================================
# Interaction Monitor
# ============================================================

class InteractionMonitor:
    """
    Monitors honeytoken/deception interactions.

    Uses SQLAlchemy 2.x async sessions.
    """

    def __init__(self, db: AsyncSession = None):
        self.db = db

    # ========================================================
    # Log Interaction
    # ========================================================

    async def log_interaction(
        self,
        honeytoken_id: int,
        source_ip: str,
        action: str,
        payload,
        risk_score: int = 0,
    ):
        """
        Persist a honeytoken interaction.
        """

        user_agent = ""

        if isinstance(payload, dict):
            user_agent = payload.get(
                "user_agent",
                "",
            )

        interaction = Interaction(
            honeytoken_id=honeytoken_id,
            source_ip=source_ip,
            action=action,
            payload=payload,
            risk_score=risk_score,
            user_agent=user_agent,
        )

        self.db.add(interaction)

        await self.db.commit()

        await self.db.refresh(interaction)

        logger.info(
            "INTERACTION: token=%s, ip=%s, "
            "action=%s, risk=%s",
            honeytoken_id,
            source_ip,
            action,
            risk_score,
        )

        return interaction

    # ========================================================
    # Repeated Access Detection
    # ========================================================

    async def check_repeated_access(
        self,
        source_ip: str,
        window_minutes: int = 10,
        threshold: int = 3,
    ) -> bool:
        """
        Detect repeated interactions from the same IP.

        Default:
            3 or more interactions
            within 10 minutes.
        """

        cutoff = (
            datetime.now(timezone.utc)
            - timedelta(
                minutes=window_minutes
            )
        )

        result = await self.db.execute(
            select(func.count())
            .select_from(Interaction)
            .where(
                Interaction.source_ip == source_ip,
                Interaction.occurred_at >= cutoff,
            )
        )

        count = result.scalar_one()

        logger.info(
            "Repeated access check: "
            "ip=%s count=%s threshold=%s",
            source_ip,
            count,
            threshold,
        )

        return count >= threshold


# ============================================================
# Attack Monitor Compatibility Wrapper
# ============================================================

class AttackMonitor(InteractionMonitor):
    """
    Compatibility class used by the DeceptionEngine.

    AttackMonitor currently inherits the interaction-monitoring
    functionality so existing imports continue to work.
    """

    pass