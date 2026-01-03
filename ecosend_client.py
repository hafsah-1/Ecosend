"""
Ecosend/GoSquared API Client

Shared module for making API calls to Ecosend (built on GoSquared).
"""

import os
import requests
import datetime

# Try to load dotenv (optional - not needed if using Streamlit secrets)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use Streamlit secrets or env vars

# === CONFIG (from Streamlit secrets or environment variables) ===
def get_credentials():
    """Get API credentials from Streamlit secrets or environment."""
    api_key = None
    site_token = None
    
    # Try Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        api_key = st.secrets.get("ecosend", {}).get("api_key")
        site_token = st.secrets.get("ecosend", {}).get("site_token")
    except Exception:
        pass
    
    # Fall back to environment variables
    if not api_key:
        api_key = os.getenv('ECOSEND_API_KEY')
    if not site_token:
        site_token = os.getenv('ECOSEND_SITE_TOKEN')
    
    return api_key, site_token

API_KEY, SITE_TOKEN = get_credentials()
BASE_URL = 'https://api.gosquared.com/people/v1'

# Validate that credentials are set
if not API_KEY or not SITE_TOKEN:
    print("⚠️  Warning: API credentials not set.")
    print("   Add to .streamlit/secrets.toml or .env file")

# === Smart Group slug mappings ===
# Faculty smart groups (slug -> display name)
FACULTY_SMART_GROUPS = {
    'fah-faculty-of-arts-humanities': 'FAH (Faculty of Arts & Humanities)',
    'fels-faculty-of-environmental-life-sciences': 'FELS (Faculty of Environmental & Life Sciences)',
    'feps-faculty-of-engineering-physical-sciences': 'FEPS (Faculty of Engineering & Physical Sciences)',
    'fm-faculty-of-medicine': 'FM (Faculty of Medicine)',
    'fss-faculty-of-social-sciences': 'FSS (Faculty of Social Sciences)',
    'professional-services': 'Professional Services'
}

# Hub smart groups (slug -> display name)
HUB_SMART_GROUPS = {
    'artificial-intelligence-ai-society': 'Artificial Intelligence (AI) & Society',
    'health-wellbeing': 'Health & Wellbeing',
    'nature-biodiversity-sustainability': 'Nature, Biodiversity & Sustainability',
    'future-cities': 'Future Cities'
}

# Reverse mappings (display name -> slug)
FACULTY_PROPERTIES = {v: k for k, v in FACULTY_SMART_GROUPS.items()}
HUB_PROPERTIES = {v: k for k, v in HUB_SMART_GROUPS.items()}

# Smart group for UoS status
UOS_SMART_GROUP = 'work-study-at-the-uos'
ALUMNI_SMART_GROUP = 'alumni-of-the-uos'

# Property for UoS status (fallback from custom properties)
UOS_STATUS_PROPERTY = 'Do you currently work or study at the UoS?'
ALUMNI_PROPERTY = 'Alumni'

# === Date 90 days ago (timezone-aware) ===
def get_since_date():
    return (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=90)).isoformat()


def _make_request(endpoint, params=None):
    """Make a GET request to the GoSquared API."""
    url = f"{BASE_URL}/{endpoint}"
    if params is None:
        params = {}
    params['api_key'] = API_KEY
    params['site_token'] = SITE_TOKEN
    
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


def get_all_people(fields=None):
    """
    Fetch all people (contacts) from Ecosend with pagination.
    
    Args:
        fields: Optional comma-separated list of fields to return
        
    Returns:
        List of all people
    """
    all_people = []
    offset = 0
    limit = 250  # Max allowed by API
    
    while True:
        params = {
            'limit': f'{offset},{limit}'
        }
        if fields:
            params['fields'] = fields
            
        data = _make_request('people', params)
        people = data.get('list', [])
        
        if not people:
            break
            
        all_people.extend(people)
        offset += len(people)
        
        # Safety check - if we got less than limit, we've reached the end
        if len(people) < limit:
            break
    
    return all_people


def get_person_feed(person_id, from_date=None, to_date=None, event_type='event'):
    """
    Get the event feed for a specific person.
    
    Args:
        person_id: The unique identifier of the person
        from_date: Optional start date
        to_date: Optional end date
        event_type: Type of events to retrieve (default: 'event')
        
    Returns:
        List of events
    """
    all_events = []
    offset = 0
    limit = 250
    
    while True:
        params = {
            'limit': f'{offset},{limit}',
            'type': event_type
        }
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
            
        data = _make_request(f'people/{person_id}/feed', params)
        events = data.get('list', [])
        
        if not events:
            break
            
        all_events.extend(events)
        offset += len(events)
        
        if len(events) < limit:
            break
    
    return all_events


def get_smartgroups():
    """Get all Smart Groups."""
    return _make_request('smartgroups')


def get_smartgroup_people(group_id, fields=None):
    """
    Get all people in a specific Smart Group.
    
    Args:
        group_id: The ID of the smart group
        fields: Optional comma-separated list of fields to return
        
    Returns:
        List of people in the smart group
    """
    all_people = []
    offset = 0
    limit = 250
    
    while True:
        params = {
            'limit': f'{offset},{limit}'
        }
        if fields:
            params['fields'] = fields
            
        data = _make_request(f'smartgroups/{group_id}/people', params)
        people = data.get('list', [])
        
        if not people:
            break
            
        all_people.extend(people)
        offset += len(people)
        
        if len(people) < limit:
            break
    
    return all_people


def get_event_types():
    """Get all tracked event types."""
    return _make_request('eventTypes')


def get_property_types():
    """Get all property types (custom and default)."""
    return _make_request('propertyTypes')


def get_custom_property_types():
    """Get only custom property types."""
    return _make_request('propertyTypes/custom')


# === Helper functions for filtering people ===

def get_custom_property(person, property_name):
    """
    Get a custom property value from a person.
    Custom properties are stored under the 'custom' key in the API response.
    """
    custom = person.get('custom', {})
    return custom.get(property_name)


def filter_people_by_custom_property(people, property_name, value=True):
    """
    Filter a list of people by a custom property value.
    
    Args:
        people: List of people objects
        property_name: Name of the custom property to filter by
        value: Value to match (default: True for boolean properties)
        
    Returns:
        List of people matching the filter
    """
    filtered = []
    for person in people:
        person_value = get_custom_property(person, property_name)
        # Handle string 'True'/'False' as well as boolean
        if isinstance(value, bool):
            if str(person_value).lower() == str(value).lower():
                filtered.append(person)
        elif person_value == value:
            filtered.append(person)
    return filtered


def get_people_by_faculty(people, faculty_name):
    """Get people belonging to a specific faculty."""
    return filter_people_by_custom_property(people, faculty_name, True)


def get_people_by_hub(people, hub_name):
    """Get people interested in a specific hub."""
    return filter_people_by_custom_property(people, hub_name, True)


def get_uos_status(person):
    """
    Check if a person currently works/studies at UoS.
    
    Returns:
        'Yes', 'No', or the value of the property
    """
    return get_custom_property(person, UOS_STATUS_PROPERTY)


def is_current_uos(person):
    """Check if person currently works/studies at UoS."""
    status = get_uos_status(person)
    return str(status).lower() == 'yes' if status else False


def is_alumni(person):
    """Check if a person is an alumni."""
    value = get_custom_property(person, ALUMNI_PROPERTY)
    return str(value).lower() == 'true' if value else False


def has_email_activity(person, since_date=None):
    """
    Check if a person has any email open activity.
    
    Note: This checks the person's event feed for email-related events.
    The actual event names may need to be adjusted based on what Ecosend tracks.
    """
    try:
        events = get_person_feed(
            person.get('id'),
            from_date=since_date,
            event_type='event'
        )
        
        # Look for email-related events
        # Common event names might be: 'Email Opened', 'Broadcast Opened', 'email_open', etc.
        email_events = ['email_open', 'Email Opened', 'Broadcast Opened', 'opened_email', 'open']
        
        for event in events:
            event_name = event.get('name', '').lower()
            if any(e.lower() in event_name for e in email_events):
                return True
                
        return False
    except Exception:
        return False


# === Test connection ===
if __name__ == "__main__":
    print("Testing Ecosend API connection...")
    try:
        # Test fetching people
        people = get_all_people()
        print(f"✅ Successfully connected! Found {len(people)} contacts.")
        
        # Show sample of properties if available
        if people:
            print("\nSample contact properties:")
            sample = people[0]
            for key in list(sample.keys())[:10]:
                print(f"  - {key}: {sample.get(key)}")
                
    except Exception as e:
        print(f"❌ Error connecting to Ecosend: {e}")
