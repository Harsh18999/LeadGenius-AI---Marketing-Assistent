import os

class Config:
    SECRET_KEY = 'xyz'  # Keep this safe!
    SESSION_TYPE = 'filesystem'
    UPLOAD_FOLDER = 'uploads'
    TOGETHER_API_KEY = os.environ['TOGETHER_API_KEY']
    
    # Email configuration
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_ADDRESS = 'kumarh18999@gmail.com'
    EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']

    @staticmethod
    def init_app(app):
        # Ensure the upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
