
# import time
# init_st = time.time() * 1000
# from flask import Flask, redirect, url_for
# from authlib.integrations.flask_client import OAuth
# init_ed = time.time() * 1000

# app = Flask(__name__)
# app.secret_key = '!secret'

# oauth = OAuth(app)

# oauth.register(
#     name='example',
#     client_id='YOUR_CLIENT_ID',
#     client_secret='YOUR_CLIENT_SECRET',
#     access_token_url='https://example.com/oauth/token',
#     authorize_url='https://example.com/oauth/authorize',
#     api_base_url='https://example.com/api/',
#     client_kwargs={'scope': 'openid email profile'}
# )
# @app.route('/')
# def index():
#     return 'Hello World!'

# @app.route('/login')
# def login():
#     redirect_uri = url_for('authorize', _external=True)
#     return oauth.example.authorize_redirect(redirect_uri)

# @app.route('/authorize')
# def authorize():
#     token = oauth.example.authorize_access_token()
#     # Store the token or use it to fetch user info
#     return 'Authorized!'

# def handle(req):
#     # don't launch the server, we just focus on the import latency
#     # app.run(debug=True, port=5001)
#     # simulate_cold_start()
#     return f'latency is {init_ed - init_st}ms'

# def simulate_cold_start():
#     import os
#     import shutil
#     pycache_dir = "/home/app"
#     for root, dirs, files in os.walk(pycache_dir):
#         if '__pycache__' in dirs:
#             dir_path = os.path.join(root, '__pycache__')
#             try:
#                 shutil.rmtree(dir_path)
#                 # print(f"Deleted directory: {dir_path}")
#             except Exception as e:
#                 print(f"Error deleting directory {dir_path}: {e}")



import time
import resource
init_st = time.time() * 1000
init_mem_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

from flask import Flask, redirect, url_for
from authlib.integrations.flask_client import OAuth
init_ed = time.time() * 1000
init_mem_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

app = Flask(__name__)
app.secret_key = '!secret'

oauth = OAuth(app)

oauth.register(
    name='example',
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    access_token_url='https://example.com/oauth/token',
    authorize_url='https://example.com/oauth/authorize',
    api_base_url='https://example.com/api/',
    client_kwargs={'scope': 'openid email profile'}
)
@app.route('/')
def index():
    return 'Hello World!'

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.example.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = oauth.example.authorize_access_token()
    # Store the token or use it to fetch user info
    return 'Authorized!'

def handle(req):
    # don't launch the server, we just focus on the import latency
    # app.run(debug=True, port=5001)
    # simulate_cold_start()
    return f'latency is {init_ed - init_st}ms, init memory usage: {init_mem_after - init_mem_before}'

def simulate_cold_start():
    import os
    import shutil
    pycache_dir = "/home/app"
    for root, dirs, files in os.walk(pycache_dir):
        if '__pycache__' in dirs:
            dir_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(dir_path)
                # print(f"Deleted directory: {dir_path}")
            except Exception as e:
                print(f"Error deleting directory {dir_path}: {e}")