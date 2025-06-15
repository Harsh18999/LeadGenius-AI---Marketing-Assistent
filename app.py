from flask import Flask
from flask_session import Session
from config import Config
from routes.auth_routes import auth_bp
from routes.email_routes import email_bp
from routes.file_routes import file_bp
from routes.llm_routes import llm_bp
from routes.other_routes import other_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SESSION_TYPE'] = 'redis' 
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = False
    app.config['SESSION_REDIS'] = redis.Redis(
    host='redis-15273.c264.ap-south-1-1.ec2.redns.redis-cloud.com',
    port=15273,
    decode_responses=False,
    username="default",
    password=os.environ['REDIS_KEY],
)
    # Initialize extensions
    Session(app)
    Config.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(llm_bp)
    app.register_blueprint(other_bp)
    
    return app
    
app = create_app()
