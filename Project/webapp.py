### importing libraries
from flask import *
import os
import numpy as np
import pandas as pd

#creating flask object
app = Flask(__name__)
app.secret_key = 'xyz'

### defining dataframe/db
user_db = pd.read_csv(r'database/user_db.csv')
event_db = pd.read_csv(r'database/event_db.csv')


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
    print(login_email, login_pswd)
    return '''<script>alert('Logging In');window.location='/'</script>'''

#sign up page route
@app.route('/sign_up')
def signup():
    return render_template('sign_up.html')

#sign up funtion route
@app.route('/signing_up', methods = ['post'])
def signing_up():
    signup_fname = request.form['sign-up_fname']
    signup_lname = request.form['sign-up_lname']
    signup_email = request.form['sign-up_email']
    signup_phone = request.form['sign-up_phone']
    signup_pswd1 = request.form['sign-up_pswd-1']
    signup_pswd2 = request.form['sign-up_pswd-2']
    print(signup_fname + ' ' + signup_lname, signup_email, signup_phone, signup_pswd1, signup_pswd2)
    return '''<script>alert('Signing Up');window.location='/sign_up'</script>'''

if __name__ == '__main__':
    app.run(debug=True)
