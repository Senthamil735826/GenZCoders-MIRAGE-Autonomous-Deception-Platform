import json
import socket
from datetime import datetime
import geoip2.database
import requests

class TelemetryCollector:
    
    @staticmethod
    def collect_http_request(request_data):
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'source_ip': request_data.get('source_ip'),
            'method': request_data.get('method'),
            'path': request_data.get('path'),
            'user_agent': request_data.get('user_agent', ''),
            'headers': request_data.get('headers', {}),
            'payload': request_data.get('payload', '')
        }
    
    @staticmethod
    def calculate_risk_score(telemetry):
        score = 0
        indicators = []
        
        suspicious_agents = ['sqlmap', 'nmap', 'nikto', 'metasploit', 'hydra']
        ua = telemetry.get('user_agent', '').lower()
        for sus in suspicious_agents:
            if sus in ua:
                score += 30
                indicators.append(f"Suspicious tool: {sus}")
        
        suspicious_paths = ['/admin', '/backup', '/.env', '/wp-admin', '/phpmyadmin']
        for path in suspicious_paths:
            if path in telemetry.get('path', '').lower():
                score += 15
                indicators.append(f"Sensitive path access: {path}")
        
        if telemetry.get('payload'):
            sql_patterns = ['union select', 'or 1=1', 'drop table', 'xp_cmdshell']
            for pattern in sql_patterns:
                if pattern in telemetry['payload'].lower():
                    score += 40
                    indicators.append(f"SQL injection attempt")
                    break
        
        if telemetry.get('method') in ['PUT', 'DELETE', 'PATCH']:
            score += 10
            indicators.append("Write operation attempt")
        
        return {
            'score': min(score, 100),
            'indicators': indicators,
            'severity': 'critical' if score >= 70 else 'high' if score >= 40 else 'medium' if score >= 20 else 'low'
        }
    
    @staticmethod
    def get_geo_info(ip_address):
        try:
            response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=2)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {'country': 'Unknown', 'city': 'Unknown'}