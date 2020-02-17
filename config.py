import os
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "secret_string"
    # make sure the cookies file not to be hacked by hacker
    
    MONGODB_SETTINGS = { 'db': 'Activity', 
        'host':'mongodb://localhost:27017/Activity'
    }