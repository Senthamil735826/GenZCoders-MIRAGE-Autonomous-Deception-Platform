import os
import secrets

class SourceCodeDeception:
    
    @staticmethod
    def create_fake_env_file(directory):
        filepath = os.path.join(directory, ".env.production")
        content = f"""DATABASE_URL=postgresql://admin:{secrets.token_urlsafe(16)}@db.internal:5432/production
AWS_ACCESS_KEY_ID=AKIA{secrets.token_hex(16).upper()}
AWS_SECRET_ACCESS_KEY={secrets.token_urlsafe(40)}
JWT_SECRET={secrets.token_urlsafe(32)}
STRIPE_API_KEY=sk_live_{secrets.token_hex(24)}
GITHUB_TOKEN=ghp_{secrets.token_hex(20)}
"""
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    @staticmethod
    def create_fake_config(directory):
        filepath = os.path.join(directory, "config.prod.yaml")
        content = f"""production:
  database:
    host: prod-db.internal
    password: {secrets.token_urlsafe(20)}
  redis:
    host: cache.internal
    password: {secrets.token_urlsafe(16)}
  api_keys:
    stripe: sk_live_{secrets.token_hex(24)}
    sendgrid: SG.{secrets.token_urlsafe(22)}
"""
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    @staticmethod
    def create_fake_credentials_file(directory):
        filepath = os.path.join(directory, "credentials.json")
        content = f"""{{
  "type": "service_account",
  "project_id": "production-{secrets.token_hex(4)}",
  "private_key_id": "{secrets.token_hex(40)}",
  "private_key": "-----BEGIN PRIVATE KEY-----\\n{secrets.token_urlsafe(100)}\\n-----END PRIVATE KEY-----"
}}"""
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath