"""
Transform real Verizon Wireless and Wireline enterprise data into IIRAF format.
This script processes authentic incident data and generates all required CSV files.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import hashlib
import re

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

def load_verizon_data():
    """Load all sheets from the Verizon Excel file."""
    excel_path = r'C:\Users\pawza\Downloads\additional isues.xlsx'
    
    # Load all sheets
    sheet1 = pd.read_excel(excel_path, sheet_name='Sheet1')
    sheet2 = pd.read_excel(excel_path, sheet_name='Sheet2')
    sheet3 = pd.read_excel(excel_path, sheet_name='Sheet3')
    
    print(f"Loaded Sheet1: {len(sheet1)} rows")
    print(f"Loaded Sheet2: {len(sheet2)} rows")
    print(f"Loaded Sheet3: {len(sheet3)} rows")
    
    return sheet1, sheet2, sheet3

def determine_severity(issue_desc, resolution):
    """Determine severity based on issue keywords."""
    text = f"{issue_desc} {resolution}".lower()
    
    # Critical keywords
    critical_keywords = ['sos', 'unavailable', 'outage', 'stuck', 'hang', 'loop', 'timeout', 
                         'failure', 'dropped', 'modem unavailable', 'optical loop']
    # High keywords
    high_keywords = ['rapid', 'toggling', 'drain', 'slow', 'jitter', 'latency', 
                     'congestion', 'prioritization']
    # Medium keywords
    medium_keywords = ['intermittent', 'sync', 'lag', 'delay', 'backhaul']
    
    if any(keyword in text for keyword in critical_keywords):
        return 'Critical'
    elif any(keyword in text for keyword in high_keywords):
        return 'High'
    elif any(keyword in text for keyword in medium_keywords):
        return 'Medium'
    else:
        return 'Low'

def extract_root_cause(issue_desc, resolution):
    """Extract or infer root cause from issue and resolution."""
    text = f"{issue_desc} {resolution}".lower()
    
    # Map keywords to root causes
    root_cause_map = {
        'network settings': ['reset network', 'network settings'],
        'eSIM provisioning issue': ['esim', 'provision', 're-provision'],
        'SIM card failure': ['replace sim', 'sim card'],
        'Network configuration': ['carrier settings', 'network mode', 'cellular data'],
        'Tower congestion': ['congestion', 'tower', 'sector'],
        'Software bug': ['update to', 'software update', 'os-level'],
        'Cache corruption': ['cache', 'clear cache'],
        'Hardware failure': ['hardware replacement', 'ont replacement', 'gateway'],
        'Modem firmware issue': ['modem', 'firmware'],
        'Infrastructure issue': ['site reset', 'network engineers', 'sector'],
        'Configuration error': ['configuration', 'settings', 'toggle'],
        'IP lease issue': ['ip lease', 'lease renewal'],
        'Splitter issue': ['splitter', 'coax'],
        'Authentication failure': ['authentication', 'push activation'],
        'Service provisioning': ['feature add', 'line profile', 'provisioning']
    }
    
    for root_cause, keywords in root_cause_map.items():
        if any(keyword in text for keyword in keywords):
            return root_cause
    
    return 'Configuration error'

def categorize_application(domain, category, issue):
    """Categorize into application/module."""
    text = f"{domain} {category} {issue}".lower()
    
    if 'wireless' in text or 'mobile' in text or '5g' in text or '4g' in text or 'lte' in text:
        if 'infrastructure' in text or 'c-band' in text or 'standalone' in text:
            return '5GInfrastructure'
        return 'Wireless'
    elif 'fios' in text or 'fiber' in text or 'ont' in text or 'moca' in text:
        return 'Fios'
    elif 'home internet' in text or 'fixed wireless' in text:
        return 'HomeInternet'
    else:
        return 'Wireless'

def generate_time_to_resolve(severity):
    """Generate realistic resolution time based on severity."""
    if severity == 'Critical':
        return random.randint(120, 1440)  # 2-24 hours
    elif severity == 'High':
        return random.randint(240, 2880)  # 4-48 hours
    elif severity == 'Medium':
        return random.randint(480, 4320)  # 8-72 hours
    else:
        return random.randint(180, 5760)  # 3-96 hours

def create_incidents_from_verizon(sheet1, sheet2, sheet3):
    """Transform Verizon data into incidents.csv format."""
    incidents = []
    incident_counter = 1
    
    # Process Sheet3 (most complete data)
    print("\nProcessing Sheet3 (Device-specific issues)...")
    for idx, row in sheet3.iterrows():
        device = str(row['Device / Hardware'])
        issue_desc = str(row['Specific Issue Description'])
        resolution = str(row['Technical Resolution / Action'])
        domain = str(row['Domain'])
        
        # Create incident
        severity = determine_severity(issue_desc, resolution)
        root_cause = extract_root_cause(issue_desc, resolution)
        application = categorize_application(domain, '', issue_desc)
        
        # Generate timestamps
        created_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 330))
        time_to_resolve = generate_time_to_resolve(severity)
        resolved_date = created_date + timedelta(minutes=time_to_resolve)
        
        # Create issue summary
        issue_summary = f"{device} - {issue_desc[:50]}..." if len(issue_desc) > 50 else f"{device} - {issue_desc}"
        
        # Pattern ID (group similar issues)
        pattern_hash = hashlib.md5(f"{application}{root_cause}".encode()).hexdigest()
        pattern_id = int(pattern_hash[:8], 16) % 20 + 1
        
        incident = {
            'incident_id': f'INC{incident_counter:05d}',
            'application': application,
            'issue_summary': issue_summary,
            'issue_description': f"Customer reported: {issue_desc}. Device: {device}. Investigation revealed {root_cause.lower()}.",
            'severity': severity,
            'root_cause': root_cause,
            'resolution': resolution,
            'pattern_id': pattern_id,
            'created_at': created_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'resolved_at': resolved_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'time_to_resolve_minutes': time_to_resolve,
            'escalated': 1 if severity in ['Critical', 'High'] and random.random() > 0.6 else 0
        }
        incidents.append(incident)
        incident_counter += 1
    
    # Process Sheet1 (Category-based issues)
    print("Processing Sheet1 (Category-based issues)...")
    for idx, row in sheet1.iterrows():
        # Skip rows with null values
        if pd.isna(row['Category']) or pd.isna(row['Distinct Issue']):
            continue
            
        category = str(row['Category'])
        issue = str(row['Distinct Issue'])
        resolution = str(row['Technical Resolution / Action Taken'])
        
        severity = determine_severity(issue, resolution)
        root_cause = extract_root_cause(issue, resolution)
        application = categorize_application('', category, issue)
        
        created_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 330))
        time_to_resolve = generate_time_to_resolve(severity)
        resolved_date = created_date + timedelta(minutes=time_to_resolve)
        
        # Extract device if mentioned in issue
        device_match = re.search(r'(iPhone|Samsung|Google Pixel|Android)', issue, re.IGNORECASE)
        device = device_match.group(1) if device_match else 'Mobile Device'
        
        issue_summary = f"{category} - {issue[:60]}..." if len(issue) > 60 else f"{category} - {issue}"
        
        pattern_hash = hashlib.md5(f"{application}{root_cause}".encode()).hexdigest()
        pattern_id = int(pattern_hash[:8], 16) % 20 + 1
        
        incident = {
            'incident_id': f'INC{incident_counter:05d}',
            'application': application,
            'issue_summary': issue_summary,
            'issue_description': f"Customer reported: {issue}. Category: {category}. Investigation revealed {root_cause.lower()}.",
            'severity': severity,
            'root_cause': root_cause,
            'resolution': resolution,
            'pattern_id': pattern_id,
            'created_at': created_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'resolved_at': resolved_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'time_to_resolve_minutes': time_to_resolve,
            'escalated': 1 if severity in ['Critical', 'High'] and random.random() > 0.6 else 0
        }
        incidents.append(incident)
        incident_counter += 1
    
    # Process Sheet2 (Infrastructure issues)
    print("Processing Sheet2 (Infrastructure issues)...")
    for idx, row in sheet2.iterrows():
        category = str(row['Category'])
        issue = str(row['Distinct Issue'])
        resolution = str(row['Technical Resolution / Action Taken'])
        
        severity = determine_severity(issue, resolution)
        root_cause = extract_root_cause(issue, resolution)
        application = categorize_application('', category, issue)
        
        created_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 330))
        time_to_resolve = generate_time_to_resolve(severity)
        resolved_date = created_date + timedelta(minutes=time_to_resolve)
        
        issue_summary = f"{category} - {issue[:70]}..." if len(issue) > 70 else f"{category} - {issue}"
        
        pattern_hash = hashlib.md5(f"{application}{root_cause}".encode()).hexdigest()
        pattern_id = int(pattern_hash[:8], 16) % 20 + 1
        
        incident = {
            'incident_id': f'INC{incident_counter:05d}',
            'application': application,
            'issue_summary': issue_summary,
            'issue_description': f"Infrastructure issue reported: {issue}. Category: {category}. Root cause: {root_cause.lower()}.",
            'severity': severity,
            'root_cause': root_cause,
            'resolution': resolution,
            'pattern_id': pattern_id,
            'created_at': created_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'resolved_at': resolved_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'time_to_resolve_minutes': time_to_resolve,
            'escalated': 1 if severity in ['Critical', 'High'] and random.random() > 0.5 else 0
        }
        incidents.append(incident)
        incident_counter += 1
    
    df = pd.DataFrame(incidents)
    print(f"\nGenerated {len(df)} incidents")
    print(f"Severity distribution:\n{df['severity'].value_counts()}")
    print(f"Application distribution:\n{df['application'].value_counts()}")
    
    return df

def create_kb_articles(incidents_df):
    """Generate KB articles from unique resolution patterns."""
    kb_articles = []
    kb_counter = 1
    
    # Group by application and root cause to create unique KB articles
    grouped = incidents_df.groupby(['application', 'root_cause'])
    
    for (application, root_cause), group in grouped:
        # Get a sample resolution
        sample_resolution = group.iloc[0]['resolution']
        
        # Create KB article
        title = f"How to resolve {root_cause} in {application}"
        
        # Format resolution into steps
        content = f"""Step 1: Verify logs and confirm occurrence of {root_cause.lower()}.
Step 2: Identify impacted components and affected services.
Step 3: Apply remediation – {sample_resolution}
Step 4: Validate system behavior and monitor for recurrence.
Step 5: Document findings and close the incident."""
        
        tags = f"{application.lower()},incident,root-cause,remediation,verizon"
        
        kb_article = {
            'kb_id': f'KB{kb_counter:04d}',
            'application': application,
            'title': title,
            'content': content,
            'tags': tags,
            'created_at': '2024-01-01'
        }
        kb_articles.append(kb_article)
        kb_counter += 1
    
    df = pd.DataFrame(kb_articles)
    print(f"\nGenerated {len(df)} KB articles")
    return df

def create_chat_transcripts(incidents_df):
    """Generate realistic customer support chat transcripts."""
    chats = []
    chat_counter = 1
    
    # Customer opening messages templates
    opening_templates = [
        "Hi, I'm having an issue with my {device}. {issue}",
        "Hello, I need help. My {device} is experiencing {issue}",
        "My {device} has been having problems. {issue}",
        "I'm experiencing issues with my service. {issue}",
        "Can you help me? {issue} on my {device}"
    ]
    
    # Agent response templates
    agent_templates = [
        "Thank you for contacting Verizon support. I understand you're experiencing {issue}. Let me help you resolve this.",
        "I'm sorry to hear you're having this issue. I'll assist you in resolving {issue}.",
        "I can help you with that. Let's troubleshoot {issue} together.",
        "Thank you for reaching out. I see you're experiencing {issue}. Let me investigate this for you."
    ]
    
    troubleshooting_templates = [
        "Let's try the following steps: {resolution}",
        "Based on the diagnostics, I recommend: {resolution}",
        "Here's what we need to do: {resolution}",
        "I've identified the issue. The solution is: {resolution}"
    ]
    
    closing_templates = [
        "Is there anything else I can help you with today?",
        "Your issue has been resolved. Please let me know if you need further assistance.",
        "The problem should be fixed now. Feel free to reach out if you have any other questions.",
        "I'm glad we could resolve this for you. Have a great day!"
    ]
    
    sentiments = ['positive', 'neutral', 'negative', 'frustrated', 'satisfied']
    
    for idx, incident in incidents_df.iterrows():
        incident_id = incident['incident_id']
        issue_desc = incident['issue_description']
        resolution = incident['resolution']
        created_at = datetime.strptime(incident['created_at'], '%Y-%m-%dT%H:%M:%S')
        
        # Extract device from issue summary
        device_match = re.search(r'(iPhone[^-]*|Samsung[^-]*|Google Pixel[^-]*|Android|Mobile Device)', 
                                incident['issue_summary'])
        device = device_match.group(1).strip() if device_match else 'device'
        
        # Extract short issue description
        short_issue = incident['issue_summary'].split(' - ', 1)[1] if ' - ' in incident['issue_summary'] else incident['issue_summary']
        
        # Chat 1: Customer opening
        chats.append({
            'chat_id': f'CHAT{chat_counter:05d}',
            'incident_id': incident_id,
            'customer_message': random.choice(opening_templates).format(device=device, issue=short_issue),
            'agent_response': '',
            'timestamp': created_at.strftime('%Y-%m-%dT%H:%M:%S'),
            'sentiment': 'frustrated' if incident['severity'] in ['Critical', 'High'] else 'neutral'
        })
        chat_counter += 1
        
        # Chat 2: Agent response
        chats.append({
            'chat_id': f'CHAT{chat_counter:05d}',
            'incident_id': incident_id,
            'customer_message': '',
            'agent_response': random.choice(agent_templates).format(issue=short_issue),
            'timestamp': (created_at + timedelta(minutes=2)).strftime('%Y-%m-%dT%H:%M:%S'),
            'sentiment': 'neutral'
        })
        chat_counter += 1
        
        # Chat 3: Troubleshooting (if resolution time > 30 mins)
        if incident['time_to_resolve_minutes'] > 30:
            chats.append({
                'chat_id': f'CHAT{chat_counter:05d}',
                'incident_id': incident_id,
                'customer_message': 'Okay, what should I do?',
                'agent_response': '',
                'timestamp': (created_at + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S'),
                'sentiment': 'neutral'
            })
            chat_counter += 1
        
        # Chat 4: Resolution steps
        chats.append({
            'chat_id': f'CHAT{chat_counter:05d}',
            'incident_id': incident_id,
            'customer_message': '',
            'agent_response': random.choice(troubleshooting_templates).format(resolution=resolution[:200]),
            'timestamp': (created_at + timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%S'),
            'sentiment': 'neutral'
        })
        chat_counter += 1
        
        # Chat 5: Customer confirmation
        if random.random() > 0.3:
            chats.append({
                'chat_id': f'CHAT{chat_counter:05d}',
                'incident_id': incident_id,
                'customer_message': random.choice(['That worked! Thank you!', 'Perfect, issue resolved.', 
                                                  'Great, everything is working now.', 'Thanks for your help!']),
                'agent_response': '',
                'timestamp': (created_at + timedelta(minutes=incident['time_to_resolve_minutes'] - 5)).strftime('%Y-%m-%dT%H:%M:%S'),
                'sentiment': 'satisfied'
            })
            chat_counter += 1
        
        # Chat 6: Agent closing
        chats.append({
            'chat_id': f'CHAT{chat_counter:05d}',
            'incident_id': incident_id,
            'customer_message': '',
            'agent_response': random.choice(closing_templates),
            'timestamp': (created_at + timedelta(minutes=incident['time_to_resolve_minutes'])).strftime('%Y-%m-%dT%H:%M:%S'),
            'sentiment': 'positive'
        })
        chat_counter += 1
    
    df = pd.DataFrame(chats)
    print(f"\nGenerated {len(df)} chat messages")
    return df

def create_patterns(incidents_df):
    """Identify recurring patterns in the incident data."""
    patterns = []
    
    # Group by pattern_id to identify recurring issues
    grouped = incidents_df.groupby('pattern_id')
    
    for pattern_id, group in grouped:
        if len(group) < 2:  # Skip patterns with only 1 incident
            continue
        
        # Get most common values
        application = group['application'].mode()[0]
        root_cause = group['root_cause'].mode()[0]
        resolution = group['resolution'].mode()[0]
        
        # Create pattern name
        pattern_name = f"{application} - {root_cause}"
        
        # Description
        description = f"Recurring pattern of {root_cause.lower()} affecting {application} services. " \
                     f"Observed {len(group)} times with {group['severity'].mode()[0]} severity."
        
        pattern = {
            'pattern_id': pattern_id,
            'pattern_name': pattern_name,
            'description': description,
            'frequency': len(group),
            'affected_applications': application,
            'common_root_cause': root_cause,
            'recommended_action': resolution[:200]
        }
        patterns.append(pattern)
    
    df = pd.DataFrame(patterns)
    df = df.sort_values('frequency', ascending=False)
    print(f"\nGenerated {len(df)} patterns")
    print(f"Top 5 patterns by frequency:\n{df.head()[['pattern_name', 'frequency']]}")
    return df

def create_autoheal_logs(incidents_df):
    """Generate auto-heal recommendations based on incidents."""
    autoheal_logs = []
    heal_counter = 1
    
    # Auto-heal action types
    action_types = {
        'Network configuration': 'reset_network_settings',
        'Cache corruption': 'clear_cache',
        'eSIM provisioning issue': 'reprovision_esim',
        'Configuration error': 'apply_config_fix',
        'Modem firmware issue': 'restart_modem',
        'Software bug': 'trigger_update'
    }
    
    # Select incidents that could have auto-heal
    for idx, incident in incidents_df.iterrows():
        # 60% of incidents get auto-heal recommendation
        if random.random() > 0.4:
            root_cause = incident['root_cause']
            action_type = action_types.get(root_cause, 'manual_intervention')
            
            # Success rate based on action type
            if action_type == 'manual_intervention':
                success_rate = random.uniform(0.3, 0.6)
            else:
                success_rate = random.uniform(0.7, 0.95)
            
            executed_at = datetime.strptime(incident['created_at'], '%Y-%m-%dT%H:%M:%S') + \
                         timedelta(minutes=random.randint(5, 30))
            
            autoheal_log = {
                'heal_id': f'HEAL{heal_counter:05d}',
                'incident_id': incident['incident_id'],
                'action_type': action_type,
                'action_details': incident['resolution'][:150],
                'success_rate': round(success_rate, 2),
                'executed_at': executed_at.strftime('%Y-%m-%dT%H:%M:%S')
            }
            autoheal_logs.append(autoheal_log)
            heal_counter += 1
    
    df = pd.DataFrame(autoheal_logs)
    print(f"\nGenerated {len(df)} auto-heal logs")
    print(f"Average success rate: {df['success_rate'].mean():.2%}")
    return df

def main():
    """Main transformation pipeline."""
    print("=" * 80)
    print("VERIZON ENTERPRISE DATA TRANSFORMATION")
    print("=" * 80)
    
    # Load source data
    print("\n[1/6] Loading Verizon data from Excel...")
    sheet1, sheet2, sheet3 = load_verizon_data()
    
    # Create incidents
    print("\n[2/6] Transforming incidents...")
    incidents_df = create_incidents_from_verizon(sheet1, sheet2, sheet3)
    
    # Create KB articles
    print("\n[3/6] Generating KB articles...")
    kb_df = create_kb_articles(incidents_df)
    
    # Create chat transcripts
    print("\n[4/6] Generating chat transcripts...")
    chats_df = create_chat_transcripts(incidents_df)
    
    # Create patterns
    print("\n[5/6] Identifying patterns...")
    patterns_df = create_patterns(incidents_df)
    
    # Create autoheal logs
    print("\n[6/6] Generating auto-heal logs...")
    autoheal_df = create_autoheal_logs(incidents_df)
    
    # Save all files
    print("\n" + "=" * 80)
    print("SAVING DATA FILES")
    print("=" * 80)
    
    data_dir = r'c:\Aslam BITS\IIRAF requirement\IIRAF_PoC_Starter\data'
    
    incidents_df.to_csv(f'{data_dir}/incidents.csv', index=False)
    print(f"[OK] Saved incidents.csv ({len(incidents_df)} records)")
    
    kb_df.to_csv(f'{data_dir}/kb_articles.csv', index=False)
    print(f"[OK] Saved kb_articles.csv ({len(kb_df)} records)")
    
    chats_df.to_csv(f'{data_dir}/chat_transcripts.csv', index=False)
    print(f"[OK] Saved chat_transcripts.csv ({len(chats_df)} records)")
    
    patterns_df.to_csv(f'{data_dir}/patterns.csv', index=False)
    print(f"[OK] Saved patterns.csv ({len(patterns_df)} records)")
    
    autoheal_df.to_csv(f'{data_dir}/autoheal_logs.csv', index=False)
    print(f"[OK] Saved autoheal_logs.csv ({len(autoheal_df)} records)")
    
    print("\n" + "=" * 80)
    print("TRANSFORMATION COMPLETE!")
    print("=" * 80)
    print(f"\nTotal incidents: {len(incidents_df)}")
    print(f"Total KB articles: {len(kb_df)}")
    print(f"Total chat messages: {len(chats_df)}")
    print(f"Total patterns: {len(patterns_df)}")
    print(f"Total autoheal logs: {len(autoheal_df)}")
    print("\nAll real Verizon enterprise data has been successfully transformed!")

if __name__ == '__main__':
    main()
