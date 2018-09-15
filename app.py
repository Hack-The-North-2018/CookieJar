from flask import *
from tempfile import mkdtemp
from firebase_admin import credentials

app = Flask(__name__)

app.secret_key = 'caffeine'

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SESSION_FILE_DIR'] = mkdtemp()
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

# Firebase Database
cred = credentials.Certificate('cookiejar-tor1-firebase-adminsdk-frm0v-bfbd8235b5.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cookiejar-tor1.firebaseio.com/'
    })

root = db.reference()

@app.route('/')
def index():
    return 'Hello world!'

if __name__ == '__main__':
    app.run(debug=True)
