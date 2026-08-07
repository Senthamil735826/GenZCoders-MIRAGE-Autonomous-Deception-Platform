import json
import secrets

class CloudDeception:
    
    @staticmethod
    def create_aws_session_token():
        return {
            'session_token': 'FwoGZXIvYXdz' + secrets.token_urlsafe(800),
            'expiration': '2025-12-31T23:59:59Z',
            'role_arn': 'arn:aws:iam::123456789012:role/AdminRole'
        }
    
    @staticmethod
    def create_azure_sas_token():
        return {
            'account': 'prodstorageaccount',
            'sas_token': 'sv=2022-11-02&ss=b&srt=sco&sp=rwdlacx&se=2025-12-31&st=2024-01-01&spr=https&sig=' + secrets.token_urlsafe(64)
        }
    
    @staticmethod
    def create_gcp_service_account():
        return {
            'type': 'service_account',
            'project_id': 'gcp-prod-' + secrets.token_hex(4),
            'client_email': 'prod-sa@' + secrets.token_hex(4) + '.iam.gserviceaccount.com',
            'private_key_id': secrets.token_hex(40)
        }