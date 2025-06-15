from flask import Blueprint, request, render_template, session
import tempfile
import os
import pandas as pd
from services.file_service import get_details_from_dataframe, get_details_from_text
from services.web_scraper import scrape_company_homepage
from services.llm_service import get_response_from_llm, get_summary_prompt
import markdown

file_bp = Blueprint('file', __name__)

@file_bp.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    text_input = request.form.get('text_input', '').strip()
    
    if file and file.filename != '':
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name

        try:
            try:
                df = pd.read_csv(temp_file_path)
                info, domains = get_details_from_dataframe(df)
                session['info'] = info
                session['domains'] = list(domains)
                companies_info = {}
                for domain in domains:
                    companies_info[domain] = {}
                    companies_info[domain]['content'] = scrape_company_homepage(domain)['content']
                    summary = get_response_from_llm(
                        prompt = get_summary_prompt(companies_info[domain]['content'])
                    )
                    companies_info[domain]['summary'] = markdown.markdown(summary)

                session['companies_info'] = companies_info
                return render_template('dashboard.html', info=info, domains=list(domains), companies_info=companies_info)
            
            except Exception:
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    data = f.read(500)
                info, domains = get_details_from_text(data)
                companies_info = {}
                for domain in domains:
                    companies_info[domain] = {}
                    companies_info[domain]['content'] = scrape_company_homepage(domain)['content']
                    summary = get_response_from_llm(
                        prompt = get_summary_prompt(companies_info[domain]['content'])
                    )
                    companies_info[domain]['summary'] = markdown.markdown(summary)
                    
                session['info'] = info
                session['domains'] = list(domains)
                session['companies_info'] = companies_info
                return render_template('dashboard.html', info=info, domains=list(domains), companies_info=companies_info)
        
        finally:
            os.remove(temp_file_path)

    elif text_input:
        data = text_input[:500]
        info, domains = get_details_from_text(data) 
        companies_info = {}

        for domain in domains:
            companies_info[domain] = {}
            companies_info[domain]['content'] = ' '.join(scrape_company_homepage(domain)['content'])
            
            summary = get_response_from_llm(
                prompt = get_summary_prompt(companies_info[domain]['content'])
            )
            
            companies_info[domain]['summary'] = markdown.markdown(summary)
        
        session['info'] = info
        session['domains'] = list(domains)
        session['companies_info'] = companies_info
        return render_template('dashboard.html', info=info, domains=list(domains), companies_info=companies_info)
    
    else:
        return render_template('index.html', error='No file or text input provided')

@file_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', 
                         info=session.get('info', {}), 
                         domains=session.get('domains', []), 
                         companies_info=session.get('companies_info', {}))

@file_bp.route('/campaign')
def campaign():
    return render_template('campaign.html', 
                         info=session.get('info', {}), 
                         domains=session.get('domains', []), 
                         companies_info=session.get('companies_info', {}))
