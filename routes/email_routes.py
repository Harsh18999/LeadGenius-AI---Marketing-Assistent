from flask import Blueprint, request, jsonify, session
from services.email_service import send_email, send_bulk_emails
from services.llm_service import get_email_body_prompt, get_email_subject_prompt, get_response_from_llm

email_bp = Blueprint('email', __name__)

@email_bp.route('/generate_email', methods=['POST'])
def generate_email():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    
    try:
        domain = session['info'][email]['domain']
        summary = session['companies_info'].get(domain, {}).get('summary', '')
        body_prompt = get_email_body_prompt(content=summary)
        body = get_response_from_llm(prompt=body_prompt)
        subject_prompt = get_email_subject_prompt(email_body=body)
        subject = get_response_from_llm(prompt=subject_prompt)
        return jsonify({'success': True, 'email': {'body': body, 'subject': subject}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@email_bp.route('/send_email', methods=['POST'])
def handle_send_email():
    data = request.get_json()
    email = data.get('email')
    return send_email(email)

@email_bp.route('/send_bulk_emails', methods=['POST'])
def handle_send_bulk_emails():
    data = request.get_json()
    emails = data.get('emails', [])
    return send_bulk_emails(emails)

@email_bp.route('/save_draft', methods=['POST'])
def save_draft():
    data = request.get_json()
    email = data.get('email')
    subject = data.get('subject')
    body = data.get('body')

    if not email or not subject or not body:
        return jsonify({'success': False, 'error': 'Missing email, subject, or body.'}), 400

    info = session.get('info', {})
    
    if email in info:
        info[email]['email_draft']['subject'] = subject
        info[email]['email_draft']['body'] = body
        session['info'] = info
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Email not found.'}), 404

@email_bp.route('/get_email_draft', methods=['POST'])
def get_email_draft():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'success': False, 'error': 'Email is required.'}), 400

    info = session.get('info', {})
    
    if email in info:
        draft = info[email]['email_draft']
        return jsonify({'success': True, 'subject': draft['subject'], 'body': draft['body']})
    
    return jsonify({'success': False, 'error': 'Email not found.'}), 404

@email_bp.route('/update_email_status', methods=['POST'])
def update_email_status():
    data = request.get_json()
    email = data.get('email')
    status = data.get('status')

    if not email or not status:
        return jsonify({'success': False, 'error': 'Missing email or status.'}), 400

    info = session.get('info', {})
    
    if email in info:
        info[email]['status'] = status
        session['info'] = info
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Email not found.'}), 404