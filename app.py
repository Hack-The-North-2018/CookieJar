import firebase_admin, requests, urllib.parse, pyrebase, re
import random
import datetime
from datetime import *
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

# Firebase Database
cred = credentials.Certificate('cookiejar-tor1-firebase-adminsdk-frm0v-bfbd8235b5.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cookiejar-tor1.firebaseio.com/'
    })

root = db.reference()

# KIK

requests.post(
    'https://api.kik.com/v1/config',
    auth=('cookiejarbot', '00c611f7-35fb-4843-8e78-cef7b59ca26a'),
    headers={
        'Content-Type': 'application/json'
    },
    data=json.dumps({
        'webhook': 'https://webhook.site/4c7f9bc4-b7ea-4eea-8ba1-7ff6f0e5306e',
        'features': {
            'receiveReadReceipts': False,
            'receiveIsTyping': False,
            'manuallySendReadReceipts': False,
            'receiveDeliveryReceipts': False
        }
    })
)

response = requests.get('https://api.td-davinci.com/api/branches',
    headers = { 'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJDQlAiLCJ0ZWFtX2lkIjoiZjE1ZWU0YzctODI1YS0zOWFiLTg2ZTQtY2I1MTEyMTMzNDVkIiwiZXhwIjo5MjIzMzcyMDM2ODU0Nzc1LCJhcHBfaWQiOiIxMjUzNDUzNy0zYmZmLTRjZjMtYjVhOC1jYmUwN2NjYWU0ZWEifQ._F2YZO7kwoW4ke6Y2qVn2j4TPiLoL2W9k-tjFMcok2o' })
response_data = response.json()

'''print(response_data)'''

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def lookup(id):
    for user in db.reference('users').get():
        if db.reference('users/{0}'.format(user)).get()['id'] == id:
            info = db.reference('users/{0}'.format(user)).get()
            break
    return info

def emaillookup(email):
    for user in db.reference('users').get():
        if db.reference('users/{0}'.format(user)).get()['email'] == email:
            emailinfo = db.reference('users/{0}'.format(user)).get()
            break
    return emailinfo


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    session.clear()

    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')

        users = []
        for user in db.reference('users').get():
            userData = db.reference('users/{0}'.format(user)).get()
            users.append({
                'id': userData['id'],
                'name': userData['name'],
                'email': userData['email'],
                'password': userData['password'],
                'shares': userData['shares']
                })

        userCreds = ''
        for user in users:
            if user['email'] == email:
                userCreds = user
                break

        if not userCreds or not check_password_hash(user['password'], password):
            flash('Invalid username and/or password')
            return render_template('login.html')

        session['user_id'] = userCreds['id']

        return redirect(url_for('home'))

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

        # Determine next user id
        ids = []
        for user in db.reference('users').get():
            ids.append(int(db.reference('users/{0}'.format(user)).get()['id']))
        nextId = max(ids) + 1

        entry = {
            'id': nextId,
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'password': generate_password_hash(request.form.get('password')),
            'shares': ''
        }

        new_user = root.child('users').push(entry)

        flash('Registered!')
        return redirect(url_for("home"))

@app.route('/home')
@login_required
def home():
    userCreds = lookup(session['user_id'])

    return render_template('home.html', user = userCreds)

@app.route('/share')
@login_required
def share():
    groups = []
    for group in db.reference('shares').get():
        groupData = db.reference('shares/{0}'.format(group)).get()
        if str(session['user_id']) in groupData['ids'].split(', '):
            groups.append({
                'id': groupData['id'],
                'name': groupData['name'],
                'members': groupData['members'].split(', '),
                'names': groupData['names'].split(', '),
                'ids': groupData['ids'].split(', ')
                })

    return render_template('share.html', userGroups = groups)

@app.route('/create', methods = ['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('create.html')
    else:
        name = request.form.get('name')
        members = request.form.get('members')
        memberlist = members.split(', ')

        emails = []
        for user in db.reference('users').get():
            emails.append(db.reference('users/{0}'.format(user)).get()['email'])

        if not name:
            flash('Jar Name cannot be blank')
            return redirect(url_for('create'))
        elif not members:
            flash('Members cannot be blank')
            return redirect(url_for('create'))

        for member in memberlist:
            if member not in emails:
                flash(member + " is not a registered user")
                return redirect(url_for('create'))

        # Determine next group id
        ids = []
        for group in db.reference('shares').get():
            ids.append(int(db.reference('shares/{0}'.format(group)).get()['id']))
        nextId = max(ids) + 1

        entry = {
            'id': nextId,
            'members': lookup(session['user_id'])['email'] + ', ' + ', '.join(memberlist),
            'names': lookup(session['user_id'])['name'] + ', ' + ', '.join([emaillookup(member)['name'] for member in memberlist]),
            'ids': str(session['user_id']) + ', ' + ', '.join([str(emaillookup(member)['id']) for member in memberlist]),
            'name': name,
            'balances': '0, ' * len(memberlist) + '0'
        }

        new_group = root.child('shares').push(entry)

        return redirect(url_for('share'))


@app.route('/group/<groupId>', methods = ['GET', 'POST'])
@login_required
def group(groupId):
    if request.method == 'GET':
        members = []
        for group in db.reference('shares').get():
            groupInfo = db.reference('shares/{0}'.format(group)).get()
            print(groupInfo)
            print(groupId)
            if str(groupId) == str(groupInfo['id']):
                
                memberlist = groupInfo['members'].split(', ')
                nameslist = groupInfo['names'].split(', ')
                idslist = groupInfo['ids'].split(', ')
                balanceslist = groupInfo['balances'].split(', ')
                for i in range(len(memberlist)):
                    print(i)
                    members.append({
                        'name': nameslist[i],
                        'email': memberlist[i],
                        'id': idslist[i],
                        'balance': balanceslist[i]
                        })

                # Group info
                groupData = {
                    'name': groupInfo['name'],
                    'id': groupInfo['id'],
                    'count': str(len(members)),
                    'members': members
                }
                break
        current = {
            'name': None,
            'email': None,
            'balance': None
        }
        return render_template('group.html', group = groupData, current = current, visibility = 'hidden')
    else:
        description = request.form.get("description")
        amount = request.form.get("amount")
        
        members = []
        for group in db.reference('shares').get():
            groupInfo = db.reference('shares/{0}'.format(group)).get()
            print(groupInfo)
            if str(groupId) == str(groupInfo['id']):
                memberlist = groupInfo['members'].split(', ')
                nameslist = groupInfo['names'].split(', ')
                idslist = groupInfo['ids'].split(', ')
                balanceslist = groupInfo['balances'].split(', ')
                for i in range(len(memberlist)):
                    members.append({
                        'name': nameslist[i],
                        'email': memberlist[i],
                        'id': idslist[i],
                        'balance': balanceslist[i]
                        })

                # Group info
                groupData = {
                    'name': groupInfo['name'],
                    'id': groupInfo['id'],
                    'count': str(len(members)),
                    'members': members
                }

                break

        current = {
            'name': None,
            'email': None,
            'balance': None
        }

        payment = float(amount) / len(members)
        index = idslist.index(str(session["user_id"]))
        for i in range (len(members)):
            if (i == index):
                calc = float(balanceslist[i])
                calc += (float(amount) - payment)
                balanceslist[i] = str(calc)
            else:
                entry = {
                    "amount": payment,
                    "description": description,
                    "id_from": i+1,
                    "from": members[i]["name"],
                    "to": members[index]["name"],
                    "id_to": index+1,
                    "time": str(datetime.now()),
                    'id': str(random.randint(1,1000))
                }
                new_entry = root.child("history").push(entry)
                calc = float(balanceslist[i])
                calc -= payment
                balanceslist[i] = str(calc)

        balanceslist=", ".join(balanceslist)
        #print (balanceslist)
        for share in db.reference('shares').get():
            
            shareData = db.reference('shares/{0}'.format(share)).get()
            print (shareData['id'])
            print (groupId)
            if int(shareData['id']) == int(groupId):
                
                edit_push = db.reference("shares/{0}".format(share)).update({
                    'balances': balanceslist
                })
                return redirect(url_for("group", groupId=groupId))
                

        return render_template('group.html', group = groupData, current = current, visibility = 'hidden')

'''
@app.route('/group/<groupId>/<memberId>')
@login_required
def groupCheck(groupId, memberId):
    members = []
    for group in db.reference('shares').get():
        groupInfo = db.reference('shares/{0}'.format(group)).get()
        print(groupInfo)
        if str(groupId) == str(groupInfo['id']):
            memberlist = groupInfo['members'].split(', ')
            nameslist = groupInfo['names'].split(', ')
            idslist = groupInfo['ids'].split(', ')
            balanceslist = groupInfo['balances'].split(', ')
            for i in range(len(memberlist)):
                members.append({
                    'name': nameslist[i],
                    'email': memberlist[i],
                    'id': idslist[i],
                    'balance': balanceslist[i]
                    })
            # Group info
            groupData = {
                'name': groupInfo['name'],
                'id': groupInfo['id'],
                'count': str(len(members)),
                'members': members
            }

            index = idslist.index(memberId)
            memberemail = memberlist[index]
            membername = nameslist[index]


            break

    current = {
        'name': None,
        'email': None,
        'balance': None
    }

    requested = []
    active = []
    history = []

    return render_template('group.html', group = groupData, current = current, requested = requested, active = active, history = history, visibility = 'visible')
'''

@app.route('/history')
@login_required
def history():
    transactions = []
    for group in db.reference('history').get():
        transactionData = db.reference('history/{0}'.format(group)).get()
        if str(session['user_id']) in str(transactionData['id_from']) or str(session['user_id']) in str(transactionData['id_to']):
            transactions.append({
                'id': transactionData['id'],
                'time': transactionData['time'],
                'description': transactionData['description'],
                'from' : transactionData['from'],
                'to' : transactionData['to'],
                'amount': transactionData['amount']
                })

    return render_template('history.html', userTransactions = transactions)

@app.route('/logout')
@login_required
def logout():
    session.clear()

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
