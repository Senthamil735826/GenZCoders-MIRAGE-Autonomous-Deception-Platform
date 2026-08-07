import secrets
import hashlib
import uuid
from faker import Faker

fake = Faker()

class HoneytokenGenerator:
    
    @staticmethod
    def generate_api_key():
        prefix = "AKIA"
        random_part = secrets.token_hex(20)
        return f"{prefix}{random_part}"
    
    @staticmethod
    def generate_aws_key():
        return {
            'aws_access_key': "AKIA" + secrets.token_hex(16).upper(),
            'aws_secret_key': secrets.token_urlsafe(40)
        }
    
    @staticmethod
    def generate_jwt_token():
        header = base64_encode('{"alg":"HS256","typ":"JWT"}')
        payload = base64_encode(f'{{"sub":"{fake.user_name()}","admin":true,"iat":{int(time.time())}}}')
        signature = secrets.token_urlsafe(32)
        return f"{header}.{payload}.{signature}"
    
    @staticmethod
    def generate_database_credential():
        return {
            'host': fake.ipv4_private(),
            'port': 5432,
            'username': 'admin_' + fake.user_name(),
            'password': secrets.token_urlsafe(16),
            'database': fake.word() + '_prod'
        }
    
    @staticmethod
    def generate_ssh_key():
        return {
            'username': fake.user_name(),
            'hostname': fake.hostname(),
            'key_type': 'RSA',
            'fingerprint': hashlib.md5(secrets.token_bytes(20)).hexdigest()
        }
    
    @staticmethod
    def generate_generic_token(token_type):
        generators = {
            'api_key': HoneytokenGenerator.generate_api_key,
            'aws_credential': HoneytokenGenerator.generate_aws_key,
            'jwt': HoneytokenGenerator.generate_jwt_token,
            'db_credential': HoneytokenGenerator.generate_database_credential,
            'ssh_key': HoneytokenGenerator.generate_ssh_key,
        }
        return generators.get(token_type, lambda: secrets.token_hex(32))()

def base64_encode(data):
    import base64
    return base64.urlsafe_b64encode(data.encode()).decode().rstrip('=')

import time