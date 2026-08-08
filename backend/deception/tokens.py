"""Assembles honeytokens: artifact + trigger identity + plantable payload."""
from __future__ import annotations

from backend.config import settings
from backend.database.models import TokenType
from backend.deception import generators as g

# default sensitivity per type (1-10)
SENSITIVITY = {
    TokenType.AWS_KEY: 9,
    TokenType.GCP_KEY: 9,
    TokenType.AZURE_KEY: 9,
    TokenType.DB_CONNECTION: 10,
    TokenType.API_KEY: 7,
    TokenType.SSH_KEY: 9,
    TokenType.ENV_FILE: 8,
    TokenType.DOCUMENT: 6,
    TokenType.S3_BUCKET: 7,
    TokenType.K8S_SECRET: 9,
    TokenType.SOURCE_SECRET: 8,
    TokenType.CANARY_URL: 5,
    TokenType.FAKE_USER: 6,
}

_BUILDERS = {
    TokenType.AWS_KEY: g.aws_credentials,
    TokenType.GCP_KEY: g.gcp_service_account,
    TokenType.AZURE_KEY: g.azure_credentials,
    TokenType.DB_CONNECTION: g.db_connection_string,
    TokenType.API_KEY: g.api_key,
    TokenType.SSH_KEY: g.ssh_private_key,
    TokenType.S3_BUCKET: g.s3_bucket,
    TokenType.K8S_SECRET: g.k8s_secret,
    TokenType.FAKE_USER: g.fake_user,
    TokenType.DOCUMENT: g.fake_document,
}


def callback_url(trigger_id: str) -> str:
    return f"{settings.PUBLIC_BASE_URL.rstrip('/')}/t/{trigger_id}"


def build_artifact(token_type: str, trigger_id: str) -> dict:
    """Return the fake artifact, with the callback woven in where natural."""
    ttype = TokenType(token_type)
    cb = callback_url(trigger_id)

    if ttype == TokenType.DOCUMENT:
        artifact = g.fake_document(trigger_id, cb)
    elif ttype in _BUILDERS:
        artifact = _BUILDERS[ttype]()
    elif ttype == TokenType.ENV_FILE:
        artifact = _env_file(trigger_id)
    elif ttype == TokenType.SOURCE_SECRET:
        artifact = _source_snippet(trigger_id)
    elif ttype == TokenType.CANARY_URL:
        artifact = {"url": cb}
    else:
        artifact = {}

    artifact["_trigger_id"] = trigger_id
    artifact["_callback"] = cb
    return artifact


def _env_file(trigger_id: str) -> dict:
    aws = g.aws_credentials()
    db = g.db_connection_string()
    key = g.api_key("stripe")
    body = f"""# production environment - DO NOT COMMIT
NODE_ENV=production
DATABASE_URL={db['dsn']}
AWS_ACCESS_KEY_ID={aws['aws_access_key_id']}
AWS_SECRET_ACCESS_KEY={aws['aws_secret_access_key']}
AWS_DEFAULT_REGION={aws['region']}
STRIPE_SECRET_KEY={key['api_key']}
INTERNAL_METRICS_URL={callback_url(trigger_id)}
SESSION_SECRET={g._rand('abcdef0123456789', 64)}
"""
    return {"filename": ".env.production", "content": body}


def _source_snippet(trigger_id: str) -> dict:
    db = g.db_connection_string()
    aws = g.aws_credentials()
    body = f'''"""Legacy config loader. TODO: migrate to Vault (JIRA INFRA-2841)."""
import os
import requests

# fallback creds used by the nightly batch job
DB_DSN = os.getenv("DB_DSN", "{db['dsn']}")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "{aws['aws_access_key_id']}")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY", "{aws['aws_secret_access_key']}")

# internal telemetry - pings build status on import
def _report_build():
    try:
        requests.get("{callback_url(trigger_id)}", timeout=2)
    except Exception:
        pass
'''
    return {"filename": "config/legacy_settings.py", "language": "python", "content": body}


def default_sensitivity(token_type: str) -> int:
    try:
        return SENSITIVITY[TokenType(token_type)]
    except (ValueError, KeyError):
        return 5