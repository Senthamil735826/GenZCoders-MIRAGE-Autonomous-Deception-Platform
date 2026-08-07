import logging
from datetime import datetime

logger = logging.getLogger("mirage.deception")

FAKE_RESPONSES = {
    "/admin": {
        "status": 200,
        "body": {"page": "Admin Panel", "version": "2.1.0", "users": 142}
    },
    "/api/users": {
        "status": 200,
        "body": [
            {"id": 1, "name": "admin", "role": "superuser"},
            {"id": 2, "name": "john.doe", "role": "manager"}
        ]
    },
    "/.env": {
        "status": 200,
        "body": "DB_HOST=10.0.0.5\nDB_PASS=fake_password_123\nSECRET=not_real"
    },
    "/wp-login.php": {
        "status": 200,
        "body": "<html><title>WordPress Login</title><form>Fake Login</form></html>"
    }
}

def generate_decoy(path):
    """Return fake data to mislead attacker."""
    if path in FAKE_RESPONSES:
        logger.info(f"[HONEYPOT] Serving decoy for: {path}")
        return FAKE_RESPONSES[path]

    # Default decoy
    return {
        "status": 200,
        "body": {"server": "Apache/2.4.41", "timestamp": datetime.utcnow().isoformat()}
    }