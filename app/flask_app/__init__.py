# flask imports
from flask import Flask
import flask_monitoringdashboard as dashboard

# python imports
from datetime import timedelta
import json

# 3dvissys imports
from flask_app.vissys.routes import vissys

def get_user_id():
    """
    Used for monitoring dashboard purposes only (can be removed).
    Generates a unique user ID for a session if user is not already in a 
    session. Returning users are kicked out of sessions after about 24 hours. 
    """
    if 'user_id' not in session:
        session.permanent = True
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

def create_app():
    """
    App Constructor. Also initializes dashboard and configuration
    """
    app = Flask(__name__)
    
    app.register_blueprint(vissys)

    # dashboard setup
    app.secret_key = 'EastmostPeninsula'
    app.permanent_session_lifetime = timedelta(days=1) # used to count each daily use as a unique visit
    dashboard.config.init_from(file='/data3/lanceu/app/monitoring/config.cfg')
    dashboard.config.group_by = get_user_id
    dashboard.bind(app)

    return app