"""
Report 3: Activity per Hub Report

Generates a report showing member counts and activity per PCE Hub.
Uses Ecosend/GoSquared API with smart_groups.
"""

import datetime
import pandas as pd
from ecosend_client import (
    get_all_people,
    HUB_SMART_GROUPS
)


def get_list_members():
    """
    Get all people with their hub interests using smart_groups.
    
    Returns:
        Dict mapping emails to their data
    """
    members = {}
    
    print("Fetching all contacts from Ecosend...")
    people = get_all_people()
    print(f"Retrieved {len(people)} contacts.")
    
    for person in people:
        email = person.get('email', '').lower()
        if not email:
            continue
        
        smart_groups = person.get('smart_groups', [])
        
        # Get hub interests (using display names)
        interests = []
        for hub_slug, hub_name in HUB_SMART_GROUPS.items():
            if hub_slug in smart_groups:
                interests.append(hub_name)
        
        members[email] = {
            'interests': interests,
            'last_seen': person.get('last_seen'),
            'engaged_at': person.get('engaged_at')
        }
    
    return members, people


def get_active_emails(people):
    """Get emails of people active in the last 90 days."""
    active_emails = set()
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=90)
    
    for person in people:
        email = person.get('email', '').lower()
        if not email:
            continue
        
        last_seen = person.get('last_seen') or person.get('engaged_at')
        
        if last_seen:
            try:
                if isinstance(last_seen, str):
                    seen_date = datetime.datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                    if seen_date >= cutoff:
                        active_emails.add(email)
            except (ValueError, TypeError):
                pass
    
    return active_emails


def generate_activity_per_hub_report(export_path="hub_activity_report.xlsx"):
    """Generate the Activity per Hub Report."""
    
    # Get members with interests
    members, all_people = get_list_members()
    
    # Get active emails
    print("Analyzing email activity...")
    active_emails = get_active_emails(all_people)
    print(f"Found {len(active_emails)} active contacts (last 90 days).")
    
    # Generate summary for each hub
    summary = []
    for hub_name in HUB_SMART_GROUPS.values():
        # Get members interested in this hub
        hub_members = [email for email, data in members.items() if hub_name in data['interests']]
        active_hub_members = [email for email in hub_members if email in active_emails]
        
        total = len(hub_members)
        active = len(active_hub_members)
        rate = (active / total * 100) if total > 0 else 0
        
        summary.append({
            "Hub": hub_name,
            "Members": total,
            "Active": active,
            "Active %": f"{rate:.2f}%"
        })
    
    # Print to terminal
    print(f"\n{'Hub':45s} | Members | Active | Active %")
    print("-" * 75)
    for row in summary:
        print(f"{row['Hub']:45s} | {row['Members']:>7} | {row['Active']:>6} | {row['Active %']}")
    
    # Generate filename with date prefix (YYYYMMDD format for easy sorting)
    date_prefix = datetime.datetime.now().strftime("%Y%m%d")
    filename_with_date = f"{date_prefix}_activity_per_hub.xlsx"
    
    # Write to Excel
    df = pd.DataFrame(summary)
    df.to_excel(filename_with_date, index=False)
    print(f"\n✅ Report exported to: {filename_with_date}")
    
    return filename_with_date


# === Compatibility exports ===
def get_recent_campaigns():
    return []

def get_email_activity(campaign_id):
    return []


# === RUN ===
if __name__ == "__main__":
    generate_activity_per_hub_report()
