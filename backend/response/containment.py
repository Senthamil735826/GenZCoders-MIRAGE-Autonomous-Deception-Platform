import subprocess
import json
from datetime import datetime

class ContainmentEngine:
    
    def __init__(self, db):
        self.db = db
        self.actions_taken = []
    
    def evaluate_threat(self, threat_event):
        if threat_event['severity'] == 'critical':
            return self.full_containment(threat_event)
        elif threat_event['severity'] == 'high':
            return self.partial_containment(threat_event)
        elif threat_event['severity'] == 'medium':
            return self.monitor_only(threat_event)
        return None
    
    def full_containment(self, threat_event):
        source_ip = threat_event['source_ip']
        actions = []
        
        actions.append(self.block_ip_firewall(source_ip))
        actions.append(self.isolate_session(source_ip))
        actions.append(self.revoke_credentials(source_ip))
        actions.append(self.alert_security_team(threat_event))
        actions.append(self.snapshot_forensics(source_ip))
        
        return actions
    
    def partial_containment(self, threat_event):
        source_ip = threat_event['source_ip']
        actions = []
        actions.append(self.rate_limit_ip(source_ip))
        actions.append(self.alert_security_team(threat_event))
        return actions
    
    def monitor_only(self, threat_event):
        return [self.alert_security_team(threat_event)]
    
    def block_ip_firewall(self, ip_address):
        action = {
            'action': 'block_ip',
            'target': ip_address,
            'method': 'firewall',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'simulated'
        }
        self.actions_taken.append(action)
        # Real implementation: subprocess.run(['iptables', '-A', 'INPUT', '-s', ip_address, '-j', 'DROP'])
        return action
    
    def isolate_session(self, ip_address):
        return {
            'action': 'isolate_session',
            'target': ip_address,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def revoke_credentials(self, identifier):
        return {
            'action': 'revoke_credentials',
            'target': identifier,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def alert_security_team(self, threat_event):
        return {
            'action': 'alert_sent',
            'channels': ['email', 'siem', 'slack'],
            'event': threat_event,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def rate_limit_ip(self, ip_address):
        return {
            'action': 'rate_limit',
            'target': ip_address,
            'limit': '10 requests/minute',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def snapshot_forensics(self, ip_address):
        return {
            'action': 'forensic_snapshot',
            'target': ip_address,
            'data_collected': ['network_logs', 'process_list', 'memory_dump'],
            'timestamp': datetime.utcnow().isoformat()
        }