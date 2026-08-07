from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime
import os
import json

from database.models import db, Honeytoken, Interaction, ThreatEvent
from deception.honeytoken_generator import HoneytokenGenerator
from deception.credential_deception import CredentialDeception
from deception.document_deception import DocumentDeception
from deception.sourcecode_deception import SourceCodeDeception
from deception.cloud_deception import CloudDeception
from detection.monitor import InteractionMonitor
from detection.telemetry import TelemetryCollector
from response.containment import ContainmentEngine

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/deception.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

monitor = InteractionMonitor(db)
containment = ContainmentEngine(db)

# ============ API ENDPOINTS ============

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/honeytokens', methods=['GET'])
def list_honeytokens():
    tokens = Honeytoken.query.all()
    return jsonify([{
        'id': t.id,
        'token_type': t.token_type,
        'location': t.location,
        'status': t.status,
        'created_at': t.created_at.isoformat(),
        'triggered_at': t.triggered_at.isoformat() if t.triggered_at else None
    } for t in tokens])

@app.route('/api/honeytokens/generate', methods=['POST'])
def generate_honeytoken():
    data = request.json
    token_type = data.get('type', 'api_key')
    location = data.get('location', '/default/')
    
    generator = HoneytokenGenerator()
    token_value = generator.generate_generic_token(token_type)
    
    if isinstance(token_value, dict):
        token_value = json.dumps(token_value)
    
    token = Honeytoken(
        token_type=token_type,
        token_value=token_value,
        location=location,
        metadata=json.dumps(data.get('metadata', {}))
    )
    db.session.add(token)
    db.session.commit()
    
    socketio.emit('honeytoken_created', {'id': token.id, 'type': token_type})
    
    return jsonify({
        'id': token.id,
        'type': token_type,
        'value': token_value,
        'location': location
    }), 201

@app.route('/api/honeytokens/canary', methods=['POST'])
def deploy_canary():
    data = request.json
    target = data.get('target', 'C:\\Windows\\System32\\')
    filename = data.get('filename', 'backup_credentials.txt')
    
    filepath = os.path.join(target, filename)
    os.makedirs(target, exist_ok=True)
    
    with open(filepath, 'w') as f:
        f.write(f"Username: admin\nPassword: P@ssw0rd2024\n")
        f.write(f"API_KEY: AKIA{os.urandom(16).hex().upper()}\n")
        f.write(f"Generated: {datetime.now()}\n")
    
    token = Honeytoken(
        token_type='canary_file',
        token_value=filepath,
        location=filepath,
        status='deployed'
    )
    db.session.add(token)
    db.session.commit()
    
    return jsonify({'filepath': filepath, 'id': token.id}), 201

@app.route('/api/credentials/deploy', methods=['POST'])
def deploy_credential_deception():
    data = request.json
    target_dir = data.get('directory', './deployed_creds/')
    os.makedirs(target_dir, exist_ok=True)
    
    cred = CredentialDeception()
    files = []
    files.append(cred.create_fake_password_file(os.path.join(target_dir, 'passwords.json')))
    files.append(cred.create_fake_shadow_file(os.path.join(target_dir, 'shadow')))
    files.append(cred.create_kerberos_ticket(os.path.join(target_dir, 'ticket.krb')))
    
    return jsonify({'deployed': files}), 201

@app.route('/api/documents/generate', methods=['POST'])
def generate_documents():
    data = request.json
    doc_type = data.get('type', 'pdf')
    target = data.get('target', './deployed_docs/')
    os.makedirs(target, exist_ok=True)
    
    doc_gen = DocumentDeception()
    filepath = ''
    
    if doc_type == 'pdf':
        filepath = doc_gen.create_fake_pdf(os.path.join(target, 'financial_report.pdf'))
    elif doc_type == 'docx':
        filepath = doc_gen.create_fake_docx(os.path.join(target, 'strategic_plan.docx'))
    else:
        filepath = doc_gen.create_fake_spreadsheet(os.path.join(target, 'employee_data.csv'))
    
    token = Honeytoken(
        token_type=f'document_{doc_type}',
        token_value=filepath,
        location=filepath
    )
    db.session.add(token)
    db.session.commit()
    
    return jsonify({'filepath': filepath}), 201

@app.route('/api/cloud/deploy', methods=['POST'])
def deploy_cloud_deception():
    data = request.json
    cloud_type = data.get('type', 'aws')
    
    cloud = CloudDeception()
    if cloud_type == 'aws':
        token_data = cloud.create_aws_session_token()
    elif cloud_type == 'azure':
        token_data = cloud.create_azure_sas_token()
    else:
        token_data = cloud.create_gcp_service_account()
    
    token = Honeytoken(
        token_type=f'cloud_{cloud_type}',
        token_value=json.dumps(token_data),
        location='cloud_storage'
    )
    db.session.add(token)
    db.session.commit()
    
    return jsonify(token_data), 201

@app.route('/api/sourcecode/deploy', methods=['POST'])
def deploy_sourcecode_deception():
    data = request.json
    target = data.get('directory', './deployed_code/')
    os.makedirs(target, exist_ok=True)
    
    sc = SourceCodeDeception()
    files = []
    files.append(sc.create_fake_env_file(target))
    files.append(sc.create_fake_config(target))
    files.append(sc.create_fake_credentials_file(target))
    
    return jsonify({'deployed': files}), 201

@app.route('/api/canary/trigger', methods=['POST'])
def trigger_canary():
    """Simulate an attacker touching a honeytoken"""
    data = request.json
    source_ip = data.get('source_ip', request.remote_addr)
    action = data.get('action', 'file_access')
    
    telemetry_data = {
        'source_ip': source_ip,
        'method': data.get('method', 'GET'),
        'path': data.get('path', '/admin/backup'),
        'user_agent': data.get('user_agent', request.headers.get('User-Agent', '')),
        'headers': dict(request.headers),
        'payload': data.get('payload', '')
    }
    
    risk = TelemetryCollector.calculate_risk_score(telemetry_data)
    
    interaction = monitor.log_interaction(
        honeytoken_id=data.get('token_id', 1),
        source_ip=source_ip,
        action=action,
        payload=telemetry_data,
        risk_score=risk['score']
    )
    
    threat_event = ThreatEvent(
        event_type=action,
        severity=risk['severity'],
        description=f"Threat detected: {', '.join(risk['indicators'])}",
        source_ip=source_ip
    )
    db.session.add(threat_event)
    db.session.commit()
    
    if risk['score'] >= 40:
        actions = containment.evaluate_threat(threat_event.to_dict() if hasattr(threat_event, 'to_dict') else {
            'severity': risk['severity'],
            'source_ip': source_ip
        })
        threat_event.contained = True
        db.session.commit()
    else:
        actions = []
    
    socketio.emit('threat_detected', {
        'interaction_id': interaction.id,
        'source_ip': source_ip,
        'risk_score': risk['score'],
        'severity': risk['severity'],
        'indicators': risk['indicators'],
        'actions': actions
    })
    
    return jsonify({
        'risk_score': risk['score'],
        'severity': risk['severity'],
        'indicators': risk['indicators'],
        'actions_taken': actions
    }), 200

@app.route('/api/threats', methods=['GET'])
def get_threats():
    threats = ThreatEvent.query.order_by(ThreatEvent.timestamp.desc()).limit(50).all()
    return jsonify([{
        'id': t.id,
        'event_type': t.event_type,
        'severity': t.severity,
        'description': t.description,
        'source_ip': t.source_ip,
        'contained': t.contained,
        'timestamp': t.timestamp.isoformat()
    } for t in threats])

@app.route('/api/interactions', methods=['GET'])
def get_interactions():
    interactions = Interaction.query.order_by(Interaction.timestamp.desc()).limit(50).all()
    return jsonify([{
        'id': i.id,
        'source_ip': i.source_ip,
        'action': i.action,
        'risk_score': i.risk_score,
        'timestamp': i.timestamp.isoformat()
    } for i in interactions])

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = {
        'total_tokens': Honeytoken.query.count(),
        'active_tokens': Honeytoken.query.filter_by(status='active').count(),
        'total_interactions': Interaction.query.count(),
        'total_threats': ThreatEvent.query.count(),
        'contained_threats': ThreatEvent.query.filter_by(contained=True).count(),
        'critical_threats': ThreatEvent.query.filter_by(severity='critical').count(),
        'high_threats': ThreatEvent.query.filter_by(severity='high').count(),
        'medium_threats': ThreatEvent.query.filter_by(severity='medium').count(),
        'low_threats': ThreatEvent.query.filter_by(severity='low').count()
    }
    return jsonify(stats)

@app.route('/api/simulate-attack', methods=['POST'])
def simulate_attack():
    """Simulate various attack scenarios for testing"""
    import random
    scenarios = [
        {'action': 'sql_injection', 'user_agent': 'sqlmap/1.5', 'payload': "' OR 1=1--"},
        {'action': 'path_traversal', 'user_agent': 'Mozilla/5.0', 'path': '/../../../etc/passwd'},
        {'action': 'brute_force', 'user_agent': 'hydra/9.0', 'path': '/admin/login'},
        {'action': 'reconnaissance', 'user_agent': 'nmap/7.80', 'path': '/'},
        {'action': 'credential_stuffing', 'user_agent': 'curl/7.68', 'path': '/api/login'}
    ]
    scenario = random.choice(scenarios)
    scenario['source_ip'] = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    
    return trigger_canary()

# ============ SOCKET EVENTS ============

@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'Connected to deception platform'})

# ============ STARTUP ============

def init_db():
    with app.app_context():
        db.create_all()
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        print("[+] Database initialized")
        print("[+] Honeytokens armed")
        print("[+] Telemetry online")
        print("[+] Containment ready")

if __name__ == '__main__':
    init_db()
    print("\n" + "="*50)
    print("  AUTONOMOUS DECEPTION INTELLIGENCE PLATFORM")
    print("="*50)
    print("  Dashboard: http://localhost:5000")
    print("  API:       http://localhost:5000/api/")
    print("="*50 + "\n")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)