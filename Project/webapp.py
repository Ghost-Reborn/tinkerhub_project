### importing libraries
from collections import UserDict
from flask import *
import os
import numpy as np
import pandas as pd

#creating flask object
app = Flask(__name__)
app.secret_key = 'xyz'

### defining dataframe/db
user_db = pd.read_csv('database/user_db.csv')
event_db = pd.read_csv('database/event_db.csv')


### defining routes
#login page route
@app.route('/')
def main():
    return render_template('login.html')

#login function route
@app.route('/login', methods = ['post'])
def login():
    login_email = request.form['login-email']
    login_pswd = request.form['login-pswd']
    return '''<script>alert('Logging In');window.location='/'</script>'''

#sign up page route
@app.route('/sign_up')
def signup():
    return render_template('sign_up.html')

#sign up funtion route
@app.route('/signing_up', methods = ['post'])
def signing_up():
    signup_fname = request.form['sign_up-fname']
    signup_lname = request.form['sign_up-lname']
    signup_email = request.form['sign_up-email']
    signup_phone = request.form['sign_up-phone']
    signup_pswd1 = request.form['sign_up-pswd-1']
    signup_pswd2 = request.form['sign_up-pswd-2']
    print(user_db)
    if signup_pswd1!=signup_pswd2:
        return '''<script>alert('Passwords not Matching');window.location='/sign_up'</script>'''
    elif signup_pswd1==signup_pswd2:
        data = [{'login_id': 0, 'fName': signup_fname, 'lName': signup_lname, 'email': signup_email,
                'phone': signup_phone, 'password': signup_pswd1, 'profile_pic': 'None',
                'events_reg': [], 'events_host': []}]
        user_db.append(data, ignore_index=True, sort=False)
        print(user_db)
        # user_db.to_csv('database/event_db.csv', index=False)
        return '''<script>alert('Signing Up');window.location='/'</script>'''
    else:
        return '''<script>alert('Error');window.location='/sign_up'</script>'''

if __name__ == '__main__':
    app.run(debug=True)
