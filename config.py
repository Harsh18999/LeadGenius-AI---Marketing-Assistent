import os

class Config:
    SECRET_KEY = 'xyz'  # Keep this safe!
    SESSION_TYPE = 'filesystem'
    UPLOAD_FOLDER = 'uploads'
    TOGETHER_API_KEY = 'e5591203825e37070d6117175cb3bd247871954000e6a17659a65833bd33105f'
    
    # Email configuration
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_ADDRESS = 'kumarh18999@gmail.com'
    EMAIL_PASSWORD = 'hkqt csvi zwhi jvyy'

    @staticmethod
    def init_app(app):
        # Ensure the upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])