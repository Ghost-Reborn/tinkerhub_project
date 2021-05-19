### importing libraries
from collections import UserDict
from flask import *
import os
import numpy as np
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import *

#creating flask object
app = Flask(__name__)
app.secret_key = 'xyz'

### defining dataframe/db
global user_db, event_db
user_db = pd.read_csv('database/user_db.csv')
event_db = pd.read_csv('database/event_db.csv')


### defining routes
#login page route
@app.route('/')
def main():
    return render_template('login.html')

#sign up page route
@app.route('/sign_up')
def signup():
    return render_template('sign_up.html')

#home page route
@app.route('/home')
def home():
    if 'lid' in session:
        return render_template('home.html')
    else:
        return render_template('method_not_allowed.html')

#my events page route
@app.route('/my_events')
def my_events():
    if 'lid' in session:
        return render_template('my_events.html')
    else:
        return render_template('method_not_allowed.html')

#profile page route
@app.route('/profile')
def profile():
    if 'lid' in session:
      return render_template('profile.html')
    else:
        return render_template('method_not_allowed.html')

#create 
@app.route('/create_event')
def create_event():
    if 'lid' in session:
      return render_template('create_event.html')
    else:
        return render_template('method_not_allowed.html')

#login function route
@app.route('/login', methods = ['post'])
def login():
    login_email = request.form['login-email']
    login_pswd = request.form['login-pswd']
    if login_email not in np.array(user_db.email):
        return '''<script>alert('User not found');window.location='/'</script>'''
    if str(user_db[user_db.email == login_email].password[0]) != login_pswd:
        return '''<script>alert('Incorrect Password');window.location='/'</script>'''
    else:
        session['lid'] = user_db[user_db.email == login_email].login_id.tolist()[0]
        return '''<script>window.location='/home'</script>'''

#logout function route
@app.route('/logout')
def logout():
    session.clear()
    return '''<script>window.location='/'</script>'''

#sign up funtion route
@app.route('/signing_up', methods = ['post'])
def signing_up():
    global user_db
    signup_fname = request.form['sign_up-fname']
    signup_lname = request.form['sign_up-lname']
    signup_email = request.form['sign_up-email']
    signup_phone = request.form['sign_up-phone']
    signup_pswd1 = request.form['sign_up-pswd-1']
    signup_pswd2 = request.form['sign_up-pswd-2']
    if signup_email in np.array(user_db.email):
        return '''<script>alert('This Email is already in use');window.location='/sign_up'</script>'''
    if signup_phone in np.array(user_db.phone):
        return '''<script>alert('This Phone Number is already in use');window.location='/sign_up'</script>'''
    if signup_pswd1!=signup_pswd2:
        return '''<script>alert('Passwords not Matching');window.location='/sign_up'</script>'''
    elif signup_pswd1==signup_pswd2:
        if user_db.login_id.max()!=True and user_db.login_id.max()!=0:
            next_uid = 0
        else:
            next_uid = user_db.login_id.max() + 1
        data = [{'login_id': next_uid, 'fName': signup_fname, 'lName': signup_lname, 'email': signup_email,
                'phone': signup_phone, 'password': signup_pswd1, 'profile_pic': 'None',
                'events_reg': [], 'events_atnd': [], 'events_host': []}]
        user_db = user_db.append(data, ignore_index=True, sort=False)
        user_db.to_csv('database/user_db.csv', index=False)
        user_db = pd.read_csv('database/user_db.csv')
        return '''<script>alert('Signing Up');window.location='/'</script>'''
    else:
        return '''<script>alert('Error');window.location='/sign_up'</script>'''

#
@app.route('/event_created', methods = ['post'])
def event_created():
    if event_db.event_id.max()!=True and event_db.event_id.max()!=0:
        next_eid = 0
    else:
        next_eid = event_db.event_id.max() + 1
    create_event_title = request.form['create-event-title']
    create_event_description = request.form['create-event-description']
    create_event_banner = request.files['create-event-banner']
    if create_event_banner.filename != '':
        time = datetime.now().strftime('%Y%m%d%H%M%S')
        create_event_banner_name = str(next_eid) + time
        create_event_banner.save(os.path.join('static/images/banners', create_event_banner_name+'.png'))
    else:
        create_event_banner_name = 'banner'
    create_event_date = request.form['create-event-date']
    create_event_time1 = request.form['create-event-time1']
    create_event_time2 = request.form['create-event-time2']
    create_event_max = request.form['create-event-max_participants']
    return '''<script>window.location='/home'</script>'''

#handling error 404
@app.errorhandler(404)
def error_404(e):
    return render_template('page_notfound.html')

if __name__ == '__main__':
    app.run(debug=True)
