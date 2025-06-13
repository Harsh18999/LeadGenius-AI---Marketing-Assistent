from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import pandas as pd
import tempfile
import re
import requests
from bs4 import BeautifulSoup
import markdown
from together import Together

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
                info, domains = get_details_from_dataframe(df)
                companies_info = {}
                for domain in domains:
                    companies_info[domain] = {}
                return render_template('home.html', info=info, domains=list(domains), companies_info=companies_info)
            
            except Exception:
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    data = f.read(500)
                # You can process plain text file here if needed
                info, domains = get_details_from_text(data)
                companies_info = {}
                for domain in domains:
                    companies_info[domain] = {}
                    companies_info[domain]['content'] = scrape_company_homepage(domain)['content']
                return render_template('home.html', info=info, domains=list(domains), companies_info=companies_info)
        
        finally:
            os.remove(temp_file_path)

    elif text_input:
        # Handle plain text input
        data = text_input[:500]
        info, domains = get_details_from_text(data) 
        companies_info = {}

        # Process each domain to scrape company homepage and generate summaries
        for domain in domains:
            companies_info[domain] = {}
            companies_info[domain]['content'] = ' '.join(scrape_company_homepage(domain)['content'])

            summary = get_response_from_llm(
                prompt = get_summary_prompt(companies_info[domain]['content'])
            )
            
            companies_info[domain]['summary'] = markdown.markdown(summary)

        return render_template('home.html', info=info, domains=list(domains), companies_info=companies_info)
    
    else:
        return render_template('index.html', error='No file or text input provided')

def get_summary_prompt(content):
    """
    Function to generate a summary prompt for the LLM based on the content.
    This is a placeholder function and should be replaced with actual prompt generation logic.

    Args:
        content (str): The web content extracted from a company's website.
    Returns:
        str: A formatted prompt string for the LLM.
    """
    prompt = f'''
    Given the following web content extracted from a company's website, perform the following tasks:

    1. **About company** — In 2-3 sentences, explain their core business, products/services, or value proposition.
    2. Start with 2-3 friendly and specific sentences that acknowledge their recent work, mission, or achievements based on the content.
    3. write in bullet points, Highlight concrete problems, gaps, or growth areas in their digital presence, services, user experience, etc., that can be improved.
    4.  Offer smart and actionable suggestions to solve or address the above issues (keep them tailored and relevant).
    5.   Write a short paragraph warning about the negative impact of ignoring these issues (use a professional and persuasive tone).

    Here is the web content:
    
    """
    {content[:29000]}  
    """
    Generate the output in clearly labeled sections.
    '''
    return prompt

def get_response_from_llm(prompt, system_prompt=None):
    """
    Function to get a response from a language model (LLM) using a prompt.
    Uses Together.ai's LLaMA 3.3 70B Instruct Turbo Free model.
    """

    # Initialize Together client
    client = Together(api_key='e5591203825e37070d6117175cb3bd247871954000e6a17659a65833bd33105f')

    # Construct message list
    messages = [{"role": "user", "content": prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    # Call the LLM API
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=messages
    )

    return response.choices[0].message.content

def get_details_from_text(text):
    '''
    Extracts first name, last name, and domain from a text input containing email addresses.
    Args:
        text (str): Text input containing email addresses.
    Returns:
        tuple: A tuple containing:
            - info (list): List of dictionaries with 'first_name', 'last_name', 'domain', and 'full_email'.
            - domains (set): Set of unique domains extracted from the email addresses.
    '''
    
    info = []
    domains = set()

    # Split the text into lines
    lines = text.splitlines()
    
    for line in lines:
        email_info = extract_email_info_re(line.strip())
        domains.add(email_info['domain'])
        info.append(email_info)
    
    return info, domains
    
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

def important_links(soup, base_url):
    about_links = []
    for a in soup.find_all('a', href=True):
        if 'about' in a.text.lower() or 'about' in a['href'].lower() or 'services' in a.text.lower() or 'services' in a['href'].lower() :
            href = a['href']
            if not href.startswith('http'):
                href = base_url.rstrip('/') + '/' + href.lstrip('/')
            about_links.append(href)
    return list(set(about_links))  # unique

def scrape_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')

    return soup.text

def scrape_company_homepage(domain):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    url = f"https://{domain}"
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = []
    content.append(soup.text)

    important_link = important_links(soup, url)

    for meta_tag in important_link:
        content.append(scrape_page(meta_tag))

    return {
        "content": content,
        "important_links": important_link,
    }

@app.route('/chat', methods=['POST'])
def chat():
    import json
    data = request.get_json()
    query = data.get("query")
    domain = data.get("active_domain").replace('\n', '').replace(' ', '')
    companies_info = data.get("companies_info", {})

    if not query :
        return jsonify({"response": "Empty query received."})
    
    print(str(domain))
    system_prompt = get_bot_system_prompt(content=companies_info.get(domain, {}).get('content', ''))
    # Call Together.ai model
    try:
        reply = get_response_from_llm(
            prompt=query,
            system_prompt=system_prompt
        )
        
        return jsonify({"response": markdown.markdown(reply)})
    
    except Exception as e:
        print("LLM error:", e)
        return jsonify({"response": "Sorry, something went wrong while contacting the LLM."})

def get_bot_system_prompt(content):
    """
    Function to get the system prompt for the LLM.
    This is a placeholder function and should be replaced with actual system prompt logic.
    """
    prompt =  f"""
    You are an intelligent assistant that understands company websites. Based on the web scraped content below, answer all queries based on content you have provided about company. 

    content: {content[:29000]}

    Your answers should be clear, concise, and business-focused.
    """
    return prompt

@app.route('/generate_email', methods=['POST'])
def generate_email():
    data = request.get_json()
    domain = data.get("domain").replace('\n', '').replace(' ', '')
    companies_info = data.get("companies_info", {})

    if not domain:
        return jsonify({"email": "Invalid domain or missing info."})
    prompt = get_email_system_prompt(content=companies_info.get(domain, {}).get('content', ''))
    email = get_response_from_llm(prompt)
    return jsonify({"email": markdown.markdown(email)})

def get_email_system_prompt(content):
    """
    Function to get the system prompt for generating an email.
    This is a placeholder function and should be replaced with actual system prompt logic.
    """
    prompt = f"""
    You are a lead generation and marketing assistant working for NetWit.ca — a company that provides growth and performance services including:

    Social Media Marketing
  - SEO (Search Engine Optimization)
  - Content Marketing
  - Paid Marketing Services
  - Outdoor Advertising
  - Cloud Hosting (Shared, Managed, BulletProof VPS)
  - PowerMTA, Email Warmup, Verification, and SMTP solutions
  - WordPress Hosting, Guides, Infographics, and Whitepapers

    You are tasked with writing a **highly personalized outreach email** to a company based on their scraped website text below. Parse and understand their business model, tone, and visible issues from the audit.

    Here is the web content of targeted company:
    {content[:29000]}
    """

    return prompt

@app.route('/campaign')
def campaign():
    return render_template('campaign.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

