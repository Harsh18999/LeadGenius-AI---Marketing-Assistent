import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import jsonify, session
from config import Config

def send_email(email):
    subject = session['info'][email]['email_draft']['subject'] 
    body = session['info'][email]['email_draft']['body']

    if not email or not subject or not body:
        return jsonify({'success': False, 'error': 'Missing email, subject, or body.'}), 400

    try:
        msg = MIMEMultipart()
        msg['From'] = Config.EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.starttls()
            server.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
            server.sendmail(Config.EMAIL_ADDRESS, email, msg.as_string())
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

    return jsonify({'success': True, 'message': 'Email sent successfully.'})

def send_bulk_emails(emails):
    if not emails or not isinstance(emails, list):
        return jsonify({'success': False, 'error': 'Invalid email list.'}), 400

    sent_count = 0
    failed_count = 0
    errors = {}

    for email in emails:
        try:
            if email not in session['info']:
                errors[email] = 'No draft found'
                failed_count += 1
                continue

            subject = session['info'][email]['email_draft'].get('subject')
            body = session['info'][email]['email_draft'].get('body')

            if not subject or not body:
                errors[email] = 'Missing subject or body'
                failed_count += 1
                continue

            msg = MIMEMultipart()
            msg['From'] = Config.EMAIL_ADDRESS
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
                server.sendmail(Config.EMAIL_ADDRESS, email, msg.as_string())

            sent_count += 1

        except Exception as e:
            errors[email] = str(e)
            failed_count += 1

    return jsonify({
        'success': True,
        'sent_count': sent_count,
        'failed_count': failed_count,
        'errors': errors if errors else None
    })