from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Honeytoken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token_type = db.Column(db.String(50), nullable=False)
    token_value = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    triggered_at = db.Column(db.DateTime)
    metadata_json = db.Column(db.JSON)

class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    honeytoken_id = db.Column(db.Integer, db.ForeignKey('honeytoken.id'))
    source_ip = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    action = db.Column(db.String(100))
    payload = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    risk_score = db.Column(db.Integer, default=0)

class ThreatEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_metadata = db.Column(db.JSON)
    event_type = db.Column(db.String(100))
    severity = db.Column(db.String(20))
    description = db.Column(db.Text)
    source_ip = db.Column(db.String(45))
    contained = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)