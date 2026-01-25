"""
Report 2: Membership Breakdown Report

Generates a report showing membership breakdown per PCE Hub,
including faculty distribution and UoS/Alumni status.
Uses Ecosend/GoSquared API with smart_groups.
"""

import datetime
import pandas as pd
from ecosend_client import (
    get_all_people,
    HUB_SMART_GROUPS,
    FACULTY_SMART_GROUPS,
    UOS_SMART_GROUP,
    ALUMNI_SMART_GROUP
)


def generate_membership_breakdown_report():
    """Generate the Membership Breakdown Report."""
    
    print("Fetching all contacts from Ecosend...")
    people = get_all_people()
    print(f"Retrieved {len(people)} contacts.")
    
    # Initialize hub counts structure
    hubs_counts = {
        display_name: {
            'total': 0,
            'non_current': 0,
            'current': 0,
            'alumni': 0,
            'faculties': {
                faculty_name: {'total': 0} for faculty_name in FACULTY_SMART_GROUPS.values()
            }
        }
        for display_name in HUB_SMART_GROUPS.values()
    }
    
    # Process each person
    for person in people:
        smart_groups = person.get('smart_groups', [])
        
        # Find which hubs this person is interested in
        hubs_interested = []
        for hub_slug, hub_name in HUB_SMART_GROUPS.items():
            if hub_slug in smart_groups:
                hubs_interested.append(hub_name)
                hubs_counts[hub_name]['total'] += 1
        
        # Find which faculties this person belongs to
        for faculty_slug, faculty_name in FACULTY_SMART_GROUPS.items():
            if faculty_slug in smart_groups:
                # Add to faculty count for each hub they're in
                for hub in hubs_interested:
                    hubs_counts[hub]['faculties'][faculty_name]['total'] += 1
        
        # Check UoS status
        is_current_uos = UOS_SMART_GROUP in smart_groups
        if is_current_uos:
            for hub in hubs_interested:
                hubs_counts[hub]['current'] += 1
        else:
            for hub in hubs_interested:
                hubs_counts[hub]['non_current'] += 1
        
        # Check alumni status
        is_alumni = ALUMNI_SMART_GROUP in smart_groups
        if is_alumni:
            for hub in hubs_interested:
                hubs_counts[hub]['alumni'] += 1
    
    # Prepare report data
    report_data = []
    report_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    for hub, counts in hubs_counts.items():
        hub_data = {
            'PCE Hub': hub,
            'Total': counts['total'],
            'Non-Current UoS': counts['non_current'],
            'Current UoS': counts['current'],
            'Alumni': counts['alumni'],
            'FAH': counts['faculties'].get('FAH', {}).get('total', 0),
            'FELS': counts['faculties'].get('FELS', {}).get('total', 0),
            'FEPS': counts['faculties'].get('FEPS', {}).get('total', 0),
            'FM': counts['faculties'].get('FM', {}).get('total', 0),
            'FSS': counts['faculties'].get('FSS', {}).get('total', 0),
            'PS': counts['faculties'].get('Professional Services', {}).get('total', 0),
        }
        report_data.append(hub_data)
    
    # Calculate "All Hubs" row (totals across all contacts)
    all_hubs_row = {
        'PCE Hub': 'All Hubs',
        'Total': len(people),
        'Non-Current UoS': sum(1 for p in people if UOS_SMART_GROUP not in p.get('smart_groups', [])),
        'Current UoS': sum(1 for p in people if UOS_SMART_GROUP in p.get('smart_groups', [])),
        'Alumni': sum(1 for p in people if ALUMNI_SMART_GROUP in p.get('smart_groups', [])),
        'FAH': sum(1 for p in people if 'fah-faculty-of-arts-humanities' in p.get('smart_groups', [])),
        'FELS': sum(1 for p in people if 'fels-faculty-of-environmental-life-sciences' in p.get('smart_groups', [])),
        'FEPS': sum(1 for p in people if 'feps-faculty-of-engineering-physical-sciences' in p.get('smart_groups', [])),
        'FM': sum(1 for p in people if 'fm-faculty-of-medicine' in p.get('smart_groups', [])),
        'FSS': sum(1 for p in people if 'fss-faculty-of-social-sciences' in p.get('smart_groups', [])),
        'PS': sum(1 for p in people if 'professional-services' in p.get('smart_groups', [])),
        'Report Date': report_date
    }
    report_data.insert(0, all_hubs_row)
    
    # Generate filename with date prefix (YYYYMMDD format for easy sorting)
    date_prefix = datetime.datetime.now().strftime("%Y%m%d")
    filename_with_date = f"{date_prefix}_membership_report.xlsx"
    
    # Write to Excel
    df = pd.DataFrame(report_data)
    df.to_excel(filename_with_date, index=False)
    
    print(f"\n✅ Report exported to: {filename_with_date}")
    return filename_with_date


# === RUN ===
if __name__ == "__main__":
    generate_membership_breakdown_report()
