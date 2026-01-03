"""
Report 4: UoS vs Non-UoS Activity Report

Generates a report comparing activity between current UoS members and non-UoS members.
Uses Ecosend/GoSquared API with smart_groups.
"""

import datetime
import pandas as pd
from ecosend_client import (
    get_all_people,
    UOS_SMART_GROUP
)


def get_list_members():
    """
    Get all people classified by UoS status using smart_groups.
    
    Returns:
        Dict with 'UOS' and 'Non-UOS' sets of email addresses
    """
    members = {"UOS": set(), "Non-UOS": set()}
    
    print("Fetching all contacts from Ecosend...")
    people = get_all_people()
    print(f"Retrieved {len(people)} contacts.")
    
    for person in people:
        email = person.get('email', '').lower()
        if not email:
            continue
        
        smart_groups = person.get('smart_groups', [])
        
        if UOS_SMART_GROUP in smart_groups:
            members["UOS"].add(email)
        else:
            members["Non-UOS"].add(email)
    
    return members, people


def get_active_emails_by_status(people, uos_emails, non_uos_emails):
    """
    Get active emails classified by UoS status.
    
    Returns:
        Tuple of (active_uos_emails, active_non_uos_emails)
    """
    active_uos_emails = set()
    active_non_uos_emails = set()
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
                        if email in uos_emails:
                            active_uos_emails.add(email)
                        elif email in non_uos_emails:
                            active_non_uos_emails.add(email)
            except (ValueError, TypeError):
                pass
    
    return active_uos_emails, active_non_uos_emails


def generate_uos_non_uos_activity_report(export_path="uos_activity.xlsx"):
    """Generate the UoS vs Non-UoS Activity Report."""
    
    # Get members by UoS status
    members, all_people = get_list_members()
    print(f"List has {len(members['UOS']) + len(members['Non-UOS'])} subscribed members.")
    
    # Get active emails
    print("Analyzing email activity...")
    active_uos_emails, active_non_uos_emails = get_active_emails_by_status(
        all_people, members["UOS"], members["Non-UOS"]
    )
    
    # Calculate totals and percentages
    uos_total = len(members["UOS"])
    uos_active = len(active_uos_emails)
    non_uos_total = len(members["Non-UOS"])
    non_uos_active = len(active_non_uos_emails)
    
    uos_pct = (uos_active / uos_total * 100) if uos_total > 0 else 0
    non_uos_pct = (non_uos_active / non_uos_total * 100) if non_uos_total > 0 else 0
    
    print(f"UoS: ({uos_active} / {uos_total}) * 100 = {uos_pct:.2f}%")
    print(f"Non-UoS: ({non_uos_active} / {non_uos_total}) * 100 = {non_uos_pct:.2f}%")
    
    summary = [
        {
            "Category": "UOS",
            "Members": uos_total,
            "Active": uos_active,
            "Active %": f"{uos_pct:.2f}%"
        },
        {
            "Category": "Non-UOS",
            "Members": non_uos_total,
            "Active": non_uos_active,
            "Active %": f"{non_uos_pct:.2f}%"
        }
    ]
    
    # Print to terminal
    print(f"\n{'Category':10s} | Members | Active | Active %")
    print("-" * 42)
    for row in summary:
        print(f"{row['Category']:10s} | {row['Members']:>7} | {row['Active']:>6} | {row['Active %']}")
    
    # Generate filename with date prefix (YYYYMMDD format for easy sorting)
    date_prefix = datetime.datetime.now().strftime("%Y%m%d")
    filename_with_date = f"{date_prefix}_uos_activity.xlsx"
    
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
    generate_uos_non_uos_activity_report()
