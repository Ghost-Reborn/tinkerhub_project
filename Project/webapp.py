### importing libraries
from collections import UserDict
from flask import *
import os
import numpy as np
from numpy.core.defchararray import join
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import *

#creating flask object
app = Flask(__name__)
app.secret_key = 'xyz'

### defining dataframe/db
global user_db, event_db, joined_df
user_db = pd.read_csv('database/user_db.csv')
event_db = pd.read_csv('database/event_db.csv')

def get_joined_df():
    joined_df = event_db.merge(user_db, left_on='host_id', right_on='login_id').drop(columns=['login_id', 'email', 'phone', 'events_host', 'password', 'profile_pic', 'events_reg', 'events_atnd'], axis=1)
    name_db = user_db[['login_id', 'fName', 'lName']]
    name_db['full_name'] = name_db.fName + ' ' + name_db.lName
    name_db = name_db.drop(columns=['fName', 'lName'], axis=1)
    def get_fullName(lid):
        return name_db.full_name[name_db.login_id == lid].tolist()[0]
    reg_count_list = []
    reg_names_list = []
    atnd_names_list = []
    for i in joined_df.participants_reg:
        if i != 'None':
            reg_id = i.split()
            reg_count_list.append(len(reg_id))
            reg_name_list = []
            for j in reg_id:
                reg_name_list.append(get_fullName(int(j)))
            reg_names_list.append(reg_name_list)
        else:
            reg_names_list.append('')
            reg_count_list.append(0)
    for i in joined_df.participants_atnd:
        if i != 'None':
            atnd_id = i.split()
            atnd_name_list = []
            for j in atnd_id:
                atnd_name_list.append(get_fullName(int(j)))
            atnd_names_list.append(atnd_name_list)
        else:
            atnd_names_list.append('')
    joined_df['participants_reg_num'] = reg_count_list
    joined_df['participants_reg_name'] = reg_names_list
    joined_df['participants_atnd_name'] = atnd_names_list
    hr_start = []
    m_start = []
    hr_end = []
    m_end = []
    for i in joined_df.date_time:
        if int(i[-11:-9])>12:
            hr_start.append(str(int(i[-11:-9])-12))
            m_start.append('PM')
        else:
            hr_start.append(i[-11:-9])
            m_start.append('AM')
        if int(i[-5:-3])>12:
            hr_end.append(str(int(i[-5:-3])-12))
            m_end.append('PM')
        else:
            hr_end.append(i[-5:-3])
            m_end.append('AM')
    joined_df['hr_start'] = hr_start
    joined_df['m_start'] = m_start
    joined_df['hr_end'] = hr_end
    joined_df['m_end'] = m_end
    fill_list = []
    for i in joined_df.event_id:
        if joined_df.max_participants[i]=='None' or int(joined_df.max_participants[i]) > joined_df.participants_reg_num[i]:
            fill_list.append('Register Now')
        else:
            fill_list.append('Filled')
    joined_df['event_fill_status'] = fill_list
    return joined_df

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
        joined_df = get_joined_df()
        home_df = joined_df[joined_df.host_id != session['lid']]
        current_dt = datetime.now().strftime('%Y%m%d%H%M')
        upcomming_list = []
        for i in home_df.event_id:
            dt = home_df.date_time[home_df.event_id == i].tolist()[0]
            upcomming_list.append(dt[:4]+dt[5:7]+dt[8:10]+dt[11:13]+dt[14:16]>current_dt)
        home_df = home_df[upcomming_list]
        return render_template('home.html', vals = home_df.sort_values(by='event_id', ascending=False).to_numpy())
    else:
        return render_template('method_not_allowed.html')

#view event page route
@app.route('/view_event')
def view_event():
    selected_eid = request.args.get('se_id')
    joined_df = get_joined_df()
    selected_event = joined_df[joined_df.event_id == np.int64(selected_eid)]
    if (selected_event.event_fill_status == 'Filled').tolist()[0]:
        return '''<script>alert('This Event is Full');window.location='/home'</script>'''
    return render_template('view_event.html', vals = selected_event.to_numpy())

#create event page route
@app.route('/create_event')
def create_event():
    if 'lid' in session:
      return render_template('create_event.html')
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

#login function route
@app.route('/login', methods = ['post'])
def login():
    login_email = request.form['login-email']
    login_pswd = request.form['login-pswd']
    if login_email not in np.array(user_db.email):
        return '''<script>alert('User not found');window.location='/'</script>'''
    if str((user_db[user_db.email == login_email].password).tolist()[0]) != login_pswd:
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
        if user_db.login_id.max()>=0:
            next_uid = user_db.login_id.max() + 1
        else:
            next_uid = 0
        data = [{'login_id': next_uid, 'fName': signup_fname, 'lName': signup_lname, 'email': signup_email,
                'phone': signup_phone, 'password': signup_pswd1, 'profile_pic': 'None',
                'events_reg': 'None', 'events_atnd': 'None', 'events_host': 'None'}]
        user_db = user_db.append(data, ignore_index=True, sort=False)
        user_db.to_csv('database/user_db.csv', index=False)
        user_db = pd.read_csv('database/user_db.csv')
        return '''<script>alert('Signing Up');window.location='/'</script>'''
    else:
        return '''<script>alert('Error');window.location='/sign_up'</script>'''

#
@app.route('/event_created', methods = ['post'])
def event_created():
    global event_db
    if event_db.event_id.max()>=0:
        next_eid = event_db.event_id.max() + 1
    else:
        next_eid = 0
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
    create_event_venue = request.form['create-event-venue']
    create_event_max = request.form['create-event-max_participants']
    if create_event_max == '':
        create_event_max = 'None'
    elif int(create_event_max)<5:
            return '''<script>alert('Event should have atleast 5 members');window.location='/create_event'</script>'''
    date_time = create_event_date[:4]+create_event_date[5:7]+create_event_date[8:]+create_event_time1[:2]+create_event_time1[-2:]+create_event_time2[:2]+create_event_time2[-2:]
    time_start = date_time[-8:-4]
    time_end = date_time[-4:]
    date = date_time[:8]
    time_crnt = datetime.now().strftime('%H%M')
    date_crnt = datetime.now().strftime('%Y%m%d')
    if date_crnt>date:
        return '''<script>alert('Event Date should be after or on Current Date');window.location='/create_event'</script>'''
    if date_crnt + time_crnt > date + time_start:
        return '''<script>alert('Event Starting Time should be after Current Time');window.location='/create_event'</script>'''
    if  date + time_start > date + time_end:
        return '''<script>alert('Event Starting Time should be before Ending Time');window.location='/create_event'</script>'''
    date_time = create_event_date[:4]+'/'+create_event_date[5:7]+'/'+create_event_date[8:]+'-'+create_event_time1[:2]+':'+create_event_time1[-2:]+'-'+create_event_time2[:2]+':'+create_event_time2[-2:]
    data = [{'event_id': next_eid, 'host_id': session['lid'], 'title' : create_event_title, 'date_time' : date_time,
            'venue': create_event_venue, 'max_participants' : create_event_max, 'description' : create_event_description,
            'banner' : create_event_banner_name, 'participants_reg' : 'None', 'participants_atnd' : 'None'}]
    event_db = event_db.append(data, ignore_index=True, sort=False)
    global user_db
    if user_db[user_db.login_id == session['lid']].events_host.tolist()[0] == 'None':
        user_db.at[user_db.login_id == session['lid'], 'events_host'] = next_eid
    else:
        user_db.at[user_db.login_id == session['lid'], 'events_host'] = str(user_db.events_host[user_db['login_id'] == session['lid']].tolist()[0])+' '+str(next_eid)
    event_db.to_csv('database/event_db.csv', index=False)
    event_db = pd.read_csv('database/event_db.csv')
    user_db.to_csv('database/user_db.csv', index=False)
    user_db = pd.read_csv('database/user_db.csv')
    return '''<script>alert('Event Registered');window.location='/home'</script>'''

# register event function
@app.route('/register_event')
def register_event():
    register_eid = request.args.get('e_id')
    print(user_db)
    print(event_db)
    return '''<script>alert('Registered to Event');window.location='/home'</script>'''

#handling error 404
@app.errorhandler(404)
def error_404(e):
    return render_template('page_notfound.html')

if __name__ == '__main__':
    app.run(debug=True)
