
"""Generate synthetic dataset for IIRAF PoC"""
import pandas as pd
import os
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created directory: {DATA_DIR}")

def generate_incidents(n=50):
    data = []
    apps = ["BillingSystem", "EmailService", "VPN", "HRPortal", "CRM"]
    severities = ["Low", "Medium", "High", "Critical"]
    
    templates = [
        ("Unable to login to {app}", "Password reset required", "High"),
        ("Slow performance in {app}", "Cleared cache and restarted service", "Medium"),
        ("{app} is down", "Restarted server instance", "Critical"),
        ("Error 500 in {app}", "Checked logs, database connection timeout", "High"),
        ("Feature X not working in {app}", "Bug ticket raised", "Low"),
        ("VPN connection failed", "Reset network adapter", "High"),
        ("Email not syncing", "Reconfigured Outlook profile", "Medium"),
        ("Printer not found", "Reinstalled printer drivers", "Low")
    ]

    for i in range(1, n + 1):
        app = random.choice(apps)
        desc_template, resolution, default_sev = random.choice(templates)
        description = desc_template.format(app=app)
        
        # Add some randomness to severity
        severity = default_sev if random.random() > 0.2 else random.choice(severities)
        
        data.append({
            "id": f"INC{i:04d}",
            "description": description,
            "resolution": resolution,
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "severity": severity,
            "application": app
        })
    
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, "incidents.csv"), index=False)
    print(f"Generated {n} incidents.")

def generate_kb_articles():
    data = [
        {"id": "KB001", "title": "VPN Troubleshooting", "content": "If VPN fails, check internet connection and reset network adapter. Ensure certificate is valid.", "keywords": "vpn, network, connection"},
        {"id": "KB002", "title": "Password Reset Procedure", "content": "Go to idm.example.com, click Forgot Password, and follow email instructions.", "keywords": "password, login, account"},
        {"id": "KB003", "title": "Outlook Sync Issues", "content": "If emails are not syncing, try rebuilding the OST file or creating a new profile.", "keywords": "email, outlook, sync"},
        {"id": "KB004", "title": "Application Performance Tuning", "content": "For slow performance, clear browser cache and cookies. If issue persists, contact support.", "keywords": "slow, performance, cache"},
        {"id": "KB005", "title": "Printer Setup Guide", "content": "To add a printer, go to Devices & Printers > Add Printer. Ensure you are on the office network.", "keywords": "printer, setup, hardware"}
    ]
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, "kb_articles.csv"), index=False)
    print(f"Generated {len(data)} KB articles.")

def generate_chat_transcripts(n=20):
    data = []
    for i in range(1, n + 1):
        incident_id = f"INC{random.randint(1, 50):04d}"
        data.append({
            "id": f"CHAT{i:04d}",
            "transcript": f"User: I have an issue with my application. Agent: What seems to be the problem? User: It is very slow. Agent: Let me check.",
            "incident_id": incident_id
        })
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, "chat_transcripts.csv"), index=False)
    print(f"Generated {n} chat transcripts.")

def generate_patterns():
    data = [
        {"pattern_id": "PAT01", "description": "VPN Connection Failures", "root_cause": "Expired Certificate"},
        {"pattern_id": "PAT02", "description": "Login Timeouts", "root_cause": "LDAP Latency"},
        {"pattern_id": "PAT03", "description": "Database Connection Errors", "root_cause": "Max Pool Size Reached"}
    ]
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, "patterns.csv"), index=False)
    print(f"Generated {len(data)} patterns.")

def generate_autoheal_logs(n=30):
    data = []
    patterns = ["PAT01", "PAT02", "PAT03"]
    actions = ["Restart Service", "Clear Cache", "Reset Adapter"]
    
    for i in range(1, n + 1):
        data.append({
            "id": f"LOG{i:04d}",
            "pattern_id": random.choice(patterns),
            "action": random.choice(actions),
            "success": random.choice([0, 1]),
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 10))).isoformat()
        })
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, "autoheal_logs.csv"), index=False)
    print(f"Generated {n} autoheal logs.")

if __name__ == "__main__":
    ensure_data_dir()
    generate_incidents()
    generate_kb_articles()
    generate_chat_transcripts()
    generate_patterns()
    generate_autoheal_logs()
    print("Data generation complete.")
