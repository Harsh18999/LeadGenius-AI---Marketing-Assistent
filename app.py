from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import pandas as pd
import tempfile
import re

app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    text_input = request.form.get('text_input', '').strip()

    if file and file.filename != '':
        # Handle file upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name

        try:
            try:
                df = pd.read_csv(temp_file_path)
                data = df.head().to_dict()
                return jsonify({'message': 'CSV file uploaded and read successfully', 'data': data})
            except Exception:
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    data = f.read(500)
                return jsonify({'message': 'Text file uploaded and read successfully', 'data': data})
        finally:
            os.remove(temp_file_path)
            
    elif text_input:
        # Handle plain text input
        # Example: just return the first 500 characters
        data = text_input[:500]
        return jsonify({'message': 'Text input received successfully', 'data': data})
    else:
        return jsonify({'error': 'No file or text input provided'}), 400


def get_details_from_dataframe(data):
    '''
    Extracts first name, last name, and domain from a DataFrame containing email addresses.
    Args:
        data (pd.DataFrame): DataFrame containing a column 'email' with email addresses.
    Returns:
        tuple: A tuple containing:
            - info (list): List of dictionaries with 'first_name', 'last_name', 'domain', and 'full_email'.
            - domains (set): Set of unique domains extracted from the email addresses.
    '''
    
    info = []
    domains = set()

    for index, row in data.iterrows():
        email_info = extract_email_info_re(row['email'])
        domains.add(email_info['domain'])
        info.append(email_info)
    
    return info, domains

def extract_email_info_re(email_string):
    """
    Extracts first name, last name, and domain from an email address string using regex.

    Args:
        email_string (str): The full email address string
                            (e.g., "John Doe <john.doe@example.com>" or "john.doe@example.com").

    Returns:
        dict: A dictionary containing 'first_name', 'last_name', 'domain', and 'full_email'.
              Returns None for any field if it cannot be extracted or if the email is invalid.
    """
    # Regex to capture display name (optional) and email address
    # Group 1: Display Name (optional)
    # Group 2: Full Email Address
    # Group 3: Username (part before @) - This needs to be added as a group
    # Group 4: Domain (part after @) - This needs to be added as a group
    # Modified regex to capture username and domain as groups 3 and 4
    email_pattern = re.compile(
        r'^(?:"?([^"<]+)"?\s+)?<?(([^@]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}))>?$'
    )

    match = email_pattern.match(email_string.strip())

    if not match:
        return {
            'first_name': None,
            'last_name': None,
            'domain': None,
            'full_email': None
        }

    # Access groups based on the updated regex
    display_name_raw = match.group(1)
    full_email = match.group(2).lower() # Group 2 is now the full email address
    username = match.group(3) # Group 3 is now the username
    domain = match.group(4).lower() # Group 4 is now the domain

    first_name = None
    last_name = None

    if display_name_raw:
        # Clean up display name (remove extra quotes if any)
        display_name = display_name_raw.strip().replace('"', '')
        name_parts = display_name.split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:])
        elif len(name_parts) == 1:
            first_name = name_parts[0]
    else:
        # Fallback: Infer from username if no display name
        username_parts = re.split(r'[._-]', username)
        if len(username_parts) >= 2:
            first_name = username_parts[0]
            last_name = username_parts[-1]
        elif len(username_parts) == 1:
            first_name = username_parts[0]

    return {
        'first_name': first_name.title() if first_name else None,
        'last_name': last_name.title() if last_name else None,
        'domain': domain,
        'full_email': full_email
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

