import firebase_admin, requests, urllib.parse, pyrebase
from flask import *
from pyrebase import *
from tempfile import mkdtemp
from firebase_admin import db, credentials
from functools import wraps
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.secret_key = 'caffeine'

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SESSION_FILE_DIR'] = mkdtemp()
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

config = {
    'apiKey': "AIzaSyCGw5dUKYIfCOxIo-BDZl5Gw3yJeKdx4wM",
    'authDomain': "cookiejar-tor1.firebaseapp.com",
    'databaseURL': "https://cookiejar-tor1.firebaseio.com",
    'projectId': "cookiejar-tor1",
    'storageBucket': "cookiejar-tor1.appspot.com",
    'messagingSenderId': "496969182776"
}

firebase = initialize_app(config)

auth = firebase.auth()

# Firebase Database
cred = credentials.Certificate('cookiejar-tor1-firebase-adminsdk-frm0v-bfbd8235b5.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cookiejar-tor1.firebaseio.com/'
    })

root = db.reference()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            auth.sign_in_with_email_and_password(email, password)
            return render_template('myjarhome.html')
        except:
            return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        # Check that username is not blank
        if not email:
            flash('Email cannot be blank')
            return render_template('register.html')

        # Check email format
        elif re.search(r'[^@]+@[^@]+\.[^@]+', email) == None:
            flash('Email is invalid. Please try again.')
            return render_template('register.html')

        # Check that password is not blank
        elif not password:
            flash('Password cannot be blank')
            return render_template('register.html')

        # Check that password and confirmation match
        elif password != confirm:
            flash('Password and confirmation do not match')
            return render_template('register.html')

        user = auth.create_user_with_email_and_password(email, password)
        print (auth.get_account_info(user['idToken']))

        auth.send_email_verification(user['idToken'])

        return render_template('registered.html')

@login_required
@app.route('/home')
def home():
    return render_template('myjarhome.html')

@login_required
@app.route('/share')
def share():
    return render_template('share.html')

@login_required
@app.route('/group')
def group():
    return render_template('groupinter.html')

@login_required
@app.route('/history')
def history():
    return render_template('history.html')

if __name__ == '__main__':
    app.run(debug=True)
