import os
import secrets
from datetime import datetime

class CanaryDeployment:
    
    @staticmethod
    def create_canary_file(directory, filename, content_type="text"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w') as f:
            f.write(f"INTERNAL USE ONLY - DO NOT DISTRIBUTE\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Tracking ID: {secrets.token_hex(16)}\n\n")
            f.write(f"Content placeholder\n")
        return filepath
    
    @staticmethod
    def create_canary_urls(base_domain):
        return [
            f"https://{base_domain}/admin/backup",
            f"https://{base_domain}/internal/credentials",
            f"https://{base_domain}/api/v1/secret-keys"
        ]