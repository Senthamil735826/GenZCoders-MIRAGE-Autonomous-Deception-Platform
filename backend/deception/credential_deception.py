import json
import os
from datetime import datetime
import secrets

class CredentialDeception:
    
    @staticmethod
    def create_fake_password_file(filepath):
        fake_passwords = {
            "admin": "P@ssw0rd2024!Admin",
            "root": "RootSecure#2024",
            "db_admin": "DB_Admin_2024_Secure",
            "service_account": "Svc" + secrets.token_urlsafe(20)
        }
        with open(filepath, 'w') as f:
            json.dump(fake_passwords, f, indent=2)
        return filepath
    
    @staticmethod
    def create_fake_shadow_file(filepath):
        shadow_content = """root:$6$rounds=656000$fakehash:19000:0:99999:7:::
admin:$6$rounds=656000$fakehash2:19000:0:99999:7:::
service:$6$rounds=656000$fakehash3:19000:0:99999:7:::
"""
        with open(filepath, 'w') as f:
            f.write(shadow_content)
        return filepath
    
    @staticmethod
    def create_kerberos_ticket(filepath):
        ticket_data = {
            "principal": "admin@CORP.LOCAL",
            "realm": "CORP.LOCAL",
            "ticket": secrets.token_urlsafe(64),
            "key": secrets.token_hex(32)
        }
        with open(filepath, 'w') as f:
            json.dump(ticket_data, f, indent=2)
        return filepath