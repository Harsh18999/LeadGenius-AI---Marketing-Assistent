from flask import Blueprint, request, jsonify, session

other_bp = Blueprint('other', __name__)

@other_bp.route('/delete_leads', methods=['POST'])
def delete_company():
    data = request.get_json()
    info = session.get('info', {})
    emails = data.get('emails', [])

    for email in emails:
        if email in info:
            del info[email]
        else:
            return jsonify({'success': False, 'error': f'Email {email} not found.'}), 404
        
    session['info'] = info
    return jsonify({'success': True})