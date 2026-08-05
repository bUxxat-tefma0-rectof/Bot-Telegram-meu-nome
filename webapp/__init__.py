from flask import Flask, send_from_directory
import os

def create_app():
    app = Flask(__name__, 
                static_folder='assets',
                template_folder='.')
    
    @app.route('/app')
    def index():
        return send_from_directory('.', 'index.html')
    
    @app.route('/admin')
    def admin():
        return send_from_directory('.', 'admin.html')
    
    @app.route('/app/<path:path>')
    def serve_app(path):
        return send_from_directory('.', path)
    
    return app
