""" A simple Werkzeug web server for running the Skills Labeller API in a
container or dev/test mode.

"""

import os
from werkzeug import run_simple
from api import app

# Environment configuration
API_PORT = os.getenv('API_PORT', 8080)
API_HOST = os.getenv('API_HOSTNAME', 'skilloracle')
API_DEBUG = os.getenv('API_DEBUG', 0)

if __name__ == '__main__':
    if API_DEBUG == 1:
        reloader = True
        debugger = True
    else:
        reloader = False
        debugger = False

    run_simple(API_HOST, API_PORT, app,
               use_reloader=reloader, use_debugger=debugger)
