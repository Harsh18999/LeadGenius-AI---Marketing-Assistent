import re
import pandas as pd

def extract_email_info_re(email_string):
    email_pattern = re.compile(
        r'^(?:"?([^"<]+)"?\s+)?<?(([^@]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}))>?$'
    )

    match = email_pattern.match(email_string.strip())

    if not match:
        return {
            'first_name': '',
            'last_name': '',
            'domain': '',
            'full_email': '',
            'status': 'Pending'
        }

    display_name_raw = match.group(1)
    full_email = match.group(2).lower()
    username = match.group(3)
    domain = match.group(4).lower()

    first_name = None
    last_name = None

    if display_name_raw:
        display_name = display_name_raw.strip().replace('"', '')
        name_parts = display_name.split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:])
        elif len(name_parts) == 1:
            first_name = name_parts[0]
    else:
        username_parts = re.split(r'[._-]', username)
        if len(username_parts) >= 2:
            first_name = username_parts[0]
            last_name = username_parts[-1]
        elif len(username_parts) == 1:
            first_name = username_parts[0]
    
    return {
        'first_name': first_name.title() if first_name else '',
        'last_name': last_name.title() if last_name else '',
        'domain': domain,
        'full_email': full_email,
        'email_draft': {
            'subject': '',
            'body': ''
        },
        'status': 'Pending'
    }

def get_details_from_dataframe(data):
    info = {}
    domains = set()

    for index, row in data.iterrows():
        email_info = extract_email_info_re(row['email'])
        domains.add(email_info['domain'])
        info[email_info['full_email']] = email_info
    
    return info, domains

def get_details_from_text(text):
    info = {}
    domains = set()
    lines = text.splitlines()
    
    for line in lines:
        email_info = extract_email_info_re(line.strip())
        domains.add(email_info['domain'])
        info[email_info['full_email']] = email_info
    
    return info, domains
