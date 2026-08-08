"""
MIRAGE Deception Engine
-----------------------

Central orchestration engine for:

- Threat analysis
- Risk scoring
- Honeytoken deployment
- Credential deception
- Fake document generation
- Cloud deception
- Source-code deception
- Shadow environments
- Network containment
- Telemetry collection
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict

from . import honeytoken_generator
from . import credential_deception
from . import document_deception
from . import cloud_deception
from . import sourcecode_deception

from ..detection.monitor import AttackMonitor
from ..response.containment import NetworkController


# ============================================================
# Logger
# ============================================================

logger = logging.getLogger("mirage.deception")


# ============================================================
# Utility
# ============================================================

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================
# Risk Levels
# ============================================================

class RiskLevel(str, Enum):

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================
# Telemetry Collector
# ============================================================

class TelemetryCollector:
    """
    Lightweight telemetry collector for the MIRAGE demo.

    Stores decision telemetry in memory and can later be
    connected to SQLAlchemy / Elasticsearch / SIEM.
    """

    def __init__(self):
        self.events = []

    async def log_decision(
        self,
        attack_id: Any,
        risk_score: float,
        timestamp: datetime,
    ) -> Dict[str, Any]:

        event = {
            "attack_id": attack_id,
            "risk_score": risk_score,
            "timestamp": timestamp.isoformat(),
            "event_type": "threat_analysis",
        }

        self.events.append(event)

        logger.info(
            "Threat decision logged: attack=%s risk=%.2f",
            attack_id,
            risk_score,
        )

        return event

    def get_events(self):
        return self.events


# ============================================================
# Deception Engine
# ============================================================

class DeceptionEngine:
    """
    Autonomous Deception Orchestrator.

    Coordinates:

        Detection
            ↓
        Risk Analysis
            ↓
        Deception
            ↓
        Containment
            ↓
        Telemetry
    """

    def __init__(self):

        self.monitor = AttackMonitor()

        self.telemetry = TelemetryCollector()

        self.network_controller = NetworkController()

        self.active_shadow_environments = {}

    # ========================================================
    # Risk Calculation
    # ========================================================

    @staticmethod
    def calculate_risk(
        attack_data: dict,
    ) -> float:
        """
        Calculate risk score between 0.0 and 1.0.
        """

        score = 0.0

        # ----------------------------------------------------
        # Attack sophistication
        # ----------------------------------------------------

        sophistication_map = {
            "automated_scan": 0.20,
            "manual_recon": 0.40,
            "exploit_attempt": 0.70,
            "lateral_movement": 0.90,
            "data_exfiltration": 1.00,
        }

        attack_type = attack_data.get(
            "type",
            attack_data.get(
                "attack_type",
                "automated_scan",
            ),
        )

        score += sophistication_map.get(
            attack_type,
            0.30,
        )

        # ----------------------------------------------------
        # Target sensitivity
        # ----------------------------------------------------

        sensitive_targets = {
            "database",
            "domain_controller",
            "crown_jewel",
        }

        if attack_data.get("target") in sensitive_targets:
            score += 0.20

        # ----------------------------------------------------
        # Repeat offender
        # ----------------------------------------------------

        if attack_data.get(
            "repeat_offender",
            False,
        ):
            score += 0.10

        # ----------------------------------------------------
        # Threat intelligence match
        # ----------------------------------------------------

        if attack_data.get(
            "threat_intel_match",
            False,
        ):
            score += 0.15

        return min(
            score,
            1.0,
        )

    # ========================================================
    # Main Analysis
    # ========================================================

    async def analyze_and_respond(
        self,
        attack_data: dict,
    ) -> Dict[str, Any]:
        """
        Main autonomous decision pipeline.
        """

        risk_score = self.calculate_risk(
            attack_data
        )

        attacker_ip = attack_data.get(
            "source_ip",
            attack_data.get(
                "ip",
                "unknown",
            ),
        )

        attack_id = attack_data.get(
            "id"
        )

        # ----------------------------------------------------
        # Telemetry
        # ----------------------------------------------------

        await self.telemetry.log_decision(
            attack_id=attack_id,
            risk_score=risk_score,
            timestamp=utcnow(),
        )

        logger.info(
            "Analyzing attack from %s | risk=%.2f",
            attacker_ip,
            risk_score,
        )

        # ----------------------------------------------------
        # Critical / High Risk
        # ----------------------------------------------------

        if risk_score > 0.80:

            return await self._handle_high_risk(
                attack_data,
                risk_score,
            )

        # ----------------------------------------------------
        # Medium Risk
        # ----------------------------------------------------

        elif risk_score > 0.50:

            return await self._handle_medium_risk(
                attack_data,
                risk_score,
            )

        # ----------------------------------------------------
        # Low Risk
        # ----------------------------------------------------

        return await self._handle_low_risk(
            attack_data,
            risk_score,
        )

    # ========================================================
    # High Risk Handler
    # ========================================================

    async def _handle_high_risk(
        self,
        attack_data: dict,
        score: float,
    ) -> Dict[str, Any]:

        attacker_ip = attack_data.get(
            "source_ip",
            attack_data.get(
                "ip",
                "unknown",
            ),
        )

        # ----------------------------------------------------
        # Network isolation
        # ----------------------------------------------------

        isolation_result = (
            await self.network_controller
            .isolate_attacker(
                attacker_ip
            )
        )

        # ----------------------------------------------------
        # Shadow environment
        # ----------------------------------------------------

        shadow_env = (
            await self._deploy_shadow_clone(
                attack_data
            )
        )

        # ----------------------------------------------------
        # Persona-specific credentials
        # ----------------------------------------------------

        fake_creds = (
            credential_deception
            .generate_persona_specific_credentials(
                attacker_profile=attack_data.get(
                    "fingerprint",
                    {},
                ),
                poisoned=True,
            )
        )

        logger.warning(
            "HIGH RISK attacker isolated: %s",
            attacker_ip,
        )

        return {
            "action": "isolated_shadow_deployed",
            "risk_score": score,
            "strategy": "aggressive_containment",
            "isolation_id": isolation_result.get(
                "id"
            ),
            "shadow_environment_id": shadow_env.get(
                "id"
            ),
            "decoys_deployed": [
                "fake_credentials",
                "fake_database",
                "fake_files",
            ],
            "credentials_generated": True,
            "credential_type": (
                "persona_specific"
            ),
        }

    # ========================================================
    # Medium Risk Handler
    # ========================================================

    async def _handle_medium_risk(
        self,
        attack_data: dict,
        score: float,
    ) -> Dict[str, Any]:

        shadow_env = (
            await self._deploy_shadow_clone(
                attack_data
            )
        )

        deception_assets = (
            await self._generate_contextual_deception(
                attack_data
            )
        )

        return {
            "action": "engaged",
            "risk_score": score,
            "strategy": "shadow_clone",
            "shadow_id": shadow_env.get(
                "id"
            ),
            "assets": deception_assets,
            "engagement_duration": "30m",
        }

    # ========================================================
    # Low Risk Handler
    # ========================================================

    async def _handle_low_risk(
        self,
        attack_data: dict,
        score: float,
    ) -> Dict[str, Any]:

        tokens = []

        vector = attack_data.get(
            "vector",
            attack_data.get(
                "attack_vector"
            ),
        )

        if vector == "file_access":

            try:

                token = (
                    honeytoken_generator
                    .embed_in_document(
                        filename="salaries_2024.xlsx",
                        canary_token=True,
                    )
                )

                tokens.append(token)

            except AttributeError:

                logger.warning(
                    "embed_in_document() is not available "
                    "in honeytoken_generator"
                )

        return {
            "action": "monitoring",
            "risk_score": score,
            "strategy": "passive_collection",
            "honeytokens_dropped": len(
                tokens
            ),
            "alert_threshold": (
                "escalate_if_persistence_detected"
            ),
        }

    # ========================================================
    # Shadow Environment
    # ========================================================

    async def _deploy_shadow_clone(
        self,
        attack_data: dict,
    ) -> Dict[str, Any]:

        target = attack_data.get(
            "target",
            "generic",
        )

        attacker_ip = attack_data.get(
            "source_ip",
            attack_data.get(
                "ip",
                "unknown",
            ),
        )

        # ----------------------------------------------------
        # Cloud deception
        # ----------------------------------------------------

        try:

            infra = (
                cloud_deception
                .spawn_isolated_environment(
                    template=target,
                    monitoring=True,
                    ttl_minutes=30,
                )
            )

        except AttributeError:

            # Safe fallback for demo
            infra = {
                "id": (
                    "shadow_"
                    + str(
                        len(
                            self.active_shadow_environments
                        )
                        + 1
                    )
                ),
                "status": "simulated",
                "template": target,
            }

        # ----------------------------------------------------
        # Fake data
        # ----------------------------------------------------

        fake_data = (
            await self.generate_deceptive_content(
                attack_data
            )
        )

        environment_id = infra.get(
            "id",
            "unknown",
        )

        self.active_shadow_environments[
            environment_id
        ] = {
            "created_at": utcnow(),
            "attacker_ip": attacker_ip,
            "data": fake_data,
        }

        logger.info(
            "Shadow environment deployed: %s",
            environment_id,
        )

        return infra

    # ========================================================
    # Contextual Deception
    # ========================================================

    async def _generate_contextual_deception(
        self,
        attack_data: dict,
    ) -> Dict[str, Any]:

        return await self.generate_deceptive_content(
            attack_data
        )

    # ========================================================
    # Deceptive Content Generator
    # ========================================================

    async def generate_deceptive_content(
        self,
        attack_context: dict,
    ) -> Dict[str, Any]:

        target = attack_context.get(
            "target",
            "generic",
        )

        deception_package = {}

        # ----------------------------------------------------
        # Database
        # ----------------------------------------------------

        if target == "database":

            try:

                deception_package[
                    "schema"
                ] = (
                    document_deception
                    .generate_database_schema(
                        company_name="Mirage Corp",
                        realistic=True,
                        poisoned=True,
                    )
                )

            except AttributeError:

                deception_package[
                    "schema"
                ] = {
                    "database": "mirage_corp",
                    "tables": [
                        "users",
                        "employees",
                        "transactions",
                    ],
                    "synthetic": True,
                }

            deception_package[
                "credentials"
            ] = (
                credential_deception
                .generate_db_credentials(
                    service=attack_context.get(
                        "service",
                        "mysql",
                    ),
                    honey_hash=True,
                )
            )

        # ----------------------------------------------------
        # File Server
        # ----------------------------------------------------

        elif target == "file_server":

            documents = []

            for doc_type in [
                "financial",
                "hr",
                "source_code",
            ]:

                try:

                    doc = (
                        document_deception
                        .generate_breadcrumb_document(
                            doc_type=doc_type,
                            tracking_id=attack_context.get(
                                "id"
                            ),
                        )
                    )

                    documents.append(doc)

                except AttributeError:

                    documents.append(
                        {
                            "type": doc_type,
                            "tracking_id": (
                                attack_context.get(
                                    "id"
                                )
                            ),
                            "synthetic": True,
                        }
                    )

            deception_package[
                "documents"
            ] = documents

        # ----------------------------------------------------
        # Source Code
        # ----------------------------------------------------

        elif target == "source_code":

            try:

                deception_package[
                    "repository"
                ] = (
                    sourcecode_deception
                    .generate_fake_repo(
                        language=attack_context.get(
                            "language",
                            "python",
                        ),
                        trap_type="callback_server",
                        callback_url=(
                            "https://alert.mirage.local/trap"
                        ),
                    )
                )

            except AttributeError:

                deception_package[
                    "repository"
                ] = {
                    "language": attack_context.get(
                        "language",
                        "python",
                    ),
                    "trap_type": "callback_server",
                    "synthetic": True,
                }

        # ----------------------------------------------------
        # Cloud
        # ----------------------------------------------------

        elif target == "cloud":

            try:

                deception_package[
                    "cloud_configs"
                ] = (
                    cloud_deception
                    .generate_fake_iam_policy(
                        trigger_alert_on_use=True
                    )
                )

            except AttributeError:

                deception_package[
                    "cloud_configs"
                ] = {
                    "provider": "cloud",
                    "trigger_alert_on_use": True,
                    "synthetic": True,
                }

        # ----------------------------------------------------
        # Honeytokens
        # ----------------------------------------------------

        try:

            deception_package[
                "tracking_tokens"
            ] = (
                honeytoken_generator
                .generate_multiple(
                    count=5,
                    alert_channels=[
                        "webhook",
                        "email",
                    ],
                )
            )

        except AttributeError:

            deception_package[
                "tracking_tokens"
            ] = []

        return deception_package

    # ========================================================
    # Cleanup Shadow Environments
    # ========================================================

    async def cleanup_shadow_environments(
        self,
    ):

        current_time = utcnow()

        to_remove = []

        for (
            env_id,
            env_data,
        ) in list(
            self.active_shadow_environments.items()
        ):

            created_at = env_data.get(
                "created_at"
            )

            if not created_at:
                continue

            age_minutes = (
                (
                    current_time
                    - created_at
                ).total_seconds()
                / 60
            )

            if age_minutes > 30:

                try:

                    await cloud_deception.terminate_environment(
                        env_id
                    )

                except AttributeError:

                    logger.info(
                        "Simulated cleanup: %s",
                        env_id,
                    )

                to_remove.append(
                    env_id
                )

        for env_id in to_remove:

            del self.active_shadow_environments[
                env_id
            ]


# ============================================================
# Global Deception Engine
# ============================================================

deception_engine = DeceptionEngine()