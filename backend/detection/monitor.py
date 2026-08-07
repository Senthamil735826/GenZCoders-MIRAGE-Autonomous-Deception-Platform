import logging
from datetime import datetime

logging.basicConfig(
    filename='logs/deception.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class InteractionMonitor:
    
    def __init__(self, db):
        self.db = db
    
    def log_interaction(self, honeytoken_id, source_ip, action, payload, risk_score):
        from backend.database.models import Interaction
        
        interaction = Interaction(
            honeytoken_id=honeytoken_id,
            source_ip=source_ip,
            action=action,
            payload=payload,
            risk_score=risk_score,
            user_agent=payload.get('user_agent', '') if isinstance(payload, dict) else ''
        )
        self.db.session.add(interaction)
        self.db.session.commit()
        
        logging.info(f"INTERACTION: token={honeytoken_id}, ip={source_ip}, action={action}, risk={risk_score}")
        
        return interaction
    
    def check_repeated_access(self, source_ip, window_minutes=10):
        from backend.database.models import Interaction
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        count = Interaction.query.filter(
            Interaction.source_ip == source_ip,
            Interaction.timestamp >= cutoff
        ).count()
        
        return count >= 3