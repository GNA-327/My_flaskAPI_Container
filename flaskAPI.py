import os
from flask import Flask
from blueprints.blueprint import app_bp
import pymongo
import redis

def create_app():
    app = Flask(__name__)
    
    # Configure MongoDB and Redis
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://mongo:27017/flask_app_db')
    app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    
    # Initialize MongoClient and Redis within app context
    app.mongo_client = pymongo.MongoClient(app.config['MONGO_URI'])
    app.redis_client = redis.Redis.from_url(app.config['REDIS_URL'])
    
    # Register Blueprint
    app.register_blueprint(app_bp, url_prefix="/blueprint")
    
    return app

if __name__ == "__main__":
    os.makedirs('uploads', exist_ok=True)
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
