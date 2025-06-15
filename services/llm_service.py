from together import Together
from config import Config

client = Together()

def get_response_from_llm(prompt, system_prompt=None):
    messages = [{"role": "user", "content": prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=messages
    )

    return response.choices[0].message.content

def get_bot_system_prompt(content):
    return f"""
    You are an intelligent assistant that understands company websites. Based on the web scraped content below, answer all queries based on content you have provided about company. 

    content: {content[:29000]}

    Your answers should be clear, concise, and business-focused.
    """

def get_summary_prompt(content):
    return f'''
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

def get_email_body_prompt(content):
    return f"""
    You are a lead generation and marketing assistant working for NetWit.ca — a company that provides growth and performance services including:

    Social Media Marketing
    SEO (Search Engine Optimization)
    Content Marketing
    Paid Marketing Services
    Outdoor Advertising
    Cloud Hosting (Shared, Managed, BulletProof VPS)
    PowerMTA, Email Warmup, Verification, and SMTP solutions
    WordPress Hosting, Guides, Infographics, and Whitepapers

    Here is more company_details : 

    NetWit (NetWit Innovation Hub) is a Vancouver‑based Canadian digital marketing and lead generation agency 
    that empowers businesses with strategic, tech‑driven solutions. As a Certified Google Ads Partner, they've 
    supported over 1,000 companies in the last decade, offering services like SEO, Google Ads, social media marketing,
    SMS/email campaigns, and CRM automation. Their philosophy emphasizes innovation, adaptability,
    professionalism, and client‑centric collaboration, aiming for swift, high‑quality delivery through their "On 
    Time Service" . Led by CEO Dhiraj Chatpar, NetWit operates Mon–Fri (10 am–6 pm), is located at 
    Granville St, Vancouver, and can be reached via [sales@netwit.ca](mailto:sales@netwit.ca) or +1 604‑722‑9996.


    You are tasked with writing a **highly personalized outreach email body only** behalf of Dave Chapter CEO of netwit.ca to a company based on their scraped website text
    below. Parse and understand their business model, tone, and visible issues from the audit.

    Here is the web content of targeted company:


    {content[:29000]}
    """

def get_email_subject_prompt(email_body):
    return f"""
    You are a lead generation and marketing assistant working for NetWit.ca — a company that provides growth and performance services including:
    Social Media Marketing
    SEO (Search Engine Optimization)
    Content Marketing
    Paid Marketing Services
    Outdoor Advertising
    Cloud Hosting (Shared, Managed, BulletProof VPS)
    PowerMTA, Email Warmup, Verification, and SMTP solutions
    WordPress Hosting, Guides, Infographics, and Whitepapers

    you are tasked with give a sigle shot subject for this email -
    Here is email body:
    {email_body}
    """
