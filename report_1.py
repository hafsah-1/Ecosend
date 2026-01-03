"""
Report 1: Faculty Activity Report

Generates a report showing member counts and email activity per faculty.
Uses Ecosend/GoSquared API with smart_groups.
"""

import datetime
import pandas as pd
from ecosend_client import (
    get_all_people,
    FACULTY_SMART_GROUPS,
    get_since_date
)


def get_list_members():
    """
    Get all people grouped by faculty using smart_groups.
    
    Returns:
        Dict mapping faculty display names to sets of email addresses
    """
    # Initialize with display names
    members = {display_name: set() for display_name in FACULTY_SMART_GROUPS.values()}
    
    print("Fetching all contacts from Ecosend...")
    people = get_all_people()
    print(f"Retrieved {len(people)} contacts.")
    
    for person in people:
        email = person.get('email', '').lower()
        if not email:
            continue
        
        # Get smart_groups for this person
        smart_groups = person.get('smart_groups', [])
        
        # Check each faculty smart group
        for slug, display_name in FACULTY_SMART_GROUPS.items():
            if slug in smart_groups:
                members[display_name].add(email)
    
    return members, people


def get_active_emails(people):
    """
    Get emails of people who have been active in the last 90 days.
    Uses last_seen or engaged_at timestamps.
    """
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


def build_active_faculty_members(faculty_members, active_emails):
    """Determine which faculty members are active."""
    active_faculty_members = {faculty: set() for faculty in faculty_members}
    
    for faculty, members in faculty_members.items():
        for email in members:
            if email in active_emails:
                active_faculty_members[faculty].add(email)
    
    return active_faculty_members


def generate_faculty_activity_report(export_path="faculty_activity.xlsx"):
    """Generate the Faculty Activity Report."""
    
    # Get all members by faculty
    print("Getting subscribed members from Ecosend...")
    faculty_members, all_people = get_list_members()
    total_members = sum(len(members) for members in faculty_members.values())
    print(f"Found {total_members} faculty-assigned members.")
    
    # Get active emails
    print("Analyzing email activity...")
    active_emails = get_active_emails(all_people)
    print(f"Found {len(active_emails)} active contacts (last 90 days).")
    
    # Build active faculty members
    active_faculty_members = build_active_faculty_members(faculty_members, active_emails)
    
    # Create report data
    report_data = []
    for faculty, members in faculty_members.items():
        total = len(members)
        active = len(active_faculty_members.get(faculty, set()))
        pct_active = (active / total * 100) if total > 0 else 0
        report_data.append({
            "Faculty": faculty,
            "Total Members": total,
            "Active Members": active,
            "Active %": f"{pct_active:.2f}%"
        })
    
    # Print to terminal
    print(f"\n{'Faculty':45s} | Total | Active | Active %")
    print("-" * 75)
    for row in report_data:
        print(f"{row['Faculty']:45s} | {row['Total Members']:>5} | {row['Active Members']:>6} | {row['Active %']}")
    
    # Generate filename with date prefix (YYYYMMDD format for easy sorting)
    date_prefix = datetime.datetime.now().strftime("%Y%m%d")
    filename_with_date = f"{date_prefix}_faculty_activity.xlsx"
    
    # Write to Excel
    df = pd.DataFrame(report_data)
    df.to_excel(filename_with_date, index=False)
    print(f"\n✅ Report exported to: {filename_with_date}")
    
    return filename_with_date


# === Compatibility exports for app.py ===
def get_recent_campaigns():
    return []

def get_email_activity(campaign_id):
    return []


# === RUN ===
if __name__ == "__main__":
    generate_faculty_activity_report()
