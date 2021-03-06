### importing libraries
from collections import UserDict
from flask import *
import os
import numpy as np
from numpy.core.defchararray import count, join
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

#joining databases
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

#getting home datadrame
def get_home_df():
    joined_df = get_joined_df()
    home_df = joined_df[joined_df.host_id != np.int64(session['lid'])]
    current_dt = datetime.now().strftime('%Y%m%d%H%M')
    upcomming_list = []
    for i in home_df.event_id:
        dt = home_df.date_time[home_df.event_id == i].tolist()[0]
        upcomming_list.append(dt[:4]+dt[5:7]+dt[8:10]+dt[11:13]+dt[14:16]>current_dt)
    home_df = home_df[upcomming_list]
    in_my_list = []
    if len(home_df != 0):
        for i in home_df.event_id:
            participants_reg_list = home_df.participants_reg[home_df.event_id == i].tolist()[0]
            if participants_reg_list != 'None':
                in_my_list.append(not str(session['lid']) in participants_reg_list.split())
            else:
                in_my_list.append(True)
        home_df = home_df[in_my_list]
    return home_df

#getting my events dataframe
def get_my_events_df():
    joined_df = get_joined_df().drop('event_fill_status', axis=1)
    my_events_df = joined_df[joined_df.host_id != session['lid']]
    current_dt = datetime.now().strftime('%Y%m%d%H%M')
    live_status_list = []
    for i in my_events_df.event_id:
        dt = my_events_df.date_time[my_events_df.event_id == i].tolist()[0]
        event_date = str(dt[:4]+dt[5:7]+dt[8:10])
        if event_date > current_dt[:8]:
            live_status_list.append('Coming Soon')
        elif event_date < current_dt[:8]:
            live_status_list.append(False)
        else:
            event_start_time = str(dt[11:-9]+dt[-8:-6])
            event_end_time = str(dt[-5:-3]+dt[-2:])
            if current_dt[-4:]>event_end_time:
                live_status_list.append(False)
            elif current_dt[-4:]<event_start_time:
                current_time_ = int(current_dt[-4:-2])*60 + int(current_dt[-2:])
                start_time_ = int(event_start_time[:2])*60 + int(event_start_time[2:])
                count_down_ = start_time_ - current_time_
                count_down_hr = str(count_down_//60)
                count_down_min = str(count_down_%60)
                if len(count_down_hr)<2:
                    count_down_hr = '0'+str(count_down_hr)
                if len(count_down_min)<2:
                    count_down_min = '0'+str(count_down_min)
                live_status_list.append(count_down_hr +':'+ count_down_min)
            elif event_start_time<=current_dt[-4:]<event_end_time:
                live_status_list.append('Live')
    my_events_df['live_status'] = live_status_list
    my_events_df = my_events_df[my_events_df.live_status!=False]
    in_my_list = []
    for i in my_events_df.event_id:
        participants_reg_list = my_events_df.participants_reg[my_events_df.event_id == i].tolist()[0]
        if participants_reg_list == 'None':
            in_my_list.append(False)
        else:
            in_my_list.append(str(session['lid']) in participants_reg_list.split())
    my_events_df = my_events_df[in_my_list]
    return my_events_df

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
        home_df = get_home_df()
        if len(home_df)==0:
          return render_template('no_events_found.html')
        return render_template('home.html', vals = home_df.sort_values(by='event_id', ascending=False).to_numpy())
    else:
        return render_template('method_not_allowed.html')

#view event page route
@app.route('/view_event')
def view_event():
    if 'lid'in session:
        selected_eid = request.args.get('se_id')
        joined_df = get_joined_df()
        selected_event = joined_df[joined_df.event_id == np.int64(selected_eid)]
        if (selected_event.event_fill_status == 'Filled').tolist()[0]:
            return '''<script>alert('This Event is Full');window.location='/home'</script>'''
        return render_template('view_event.html', vals = selected_event.to_numpy())
    else:
        return render_template('method_not_allowed.html')

#view event page route
@app.route('/view_my_event')
def view_my_event():
    if 'lid' in session:
        selected_eid = request.args.get('se_id')
        my_events_df = get_my_events_df()
        selected_event = my_events_df[my_events_df.event_id == np.int64(selected_eid)]
        return render_template('view_my_event.html', vals = selected_event.to_numpy())
    else:
        return render_template('method_not_allowed.html')

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
        my_events_df = get_my_events_df()
        if len(my_events_df)==0:
            return render_template('no_events_found.html')
        return render_template('my_events.html', vals = my_events_df.sort_values(by='date_time', ascending=True).to_numpy())
    else:
        return render_template('method_not_allowed.html')

#profile page route
@app.route('/profile')
def profile():
    if 'lid' in session:
        joined_df = get_joined_df()
        user = user_db[user_db.login_id == session['lid']]
        attended = user.events_atnd.tolist()[0].split()
        attended_events = []
        if attended==['None']:
            attended_events = pd.Series([])
        else:
            for i in joined_df.event_id:
                attended_events.append(joined_df[joined_df.event_id == i].event_id.tolist()[0] in np.array(attended, dtype='int64'))
            attended_events = joined_df[attended_events]
        hosted_event = joined_df[joined_df.host_id == session['lid']]
        return render_template('profile.html', val=user.to_numpy()[0], val_atnd=attended_events.to_numpy(), val_host=hosted_event.to_numpy())
    else:
        return render_template('method_not_allowed.html')

#profile page route
@app.route('/view_profile')
def view_profile():
    if 'lid' in session:
        user_id = np.int64(request.args.get('s_lid'))
        return render_template('view_profile.html', val=user_db[user_db.login_id == user_id].to_numpy()[0])
    else:
        return render_template('method_not_allowed.html')

#view participants page route
@app.route('/view_participants')
def view_participants():
    if 'lid' in session:
        s_event_id = request.args.get('e_id')
        joined_df = get_joined_df()
        event_attendees = event_db[event_db.event_id == np.int64(s_event_id)].participants_atnd.tolist()[0].split()
        event = np.array(joined_df[joined_df.event_id == np.int64(s_event_id)])[0].tolist()
        event_attendees_name = []
        if event_attendees!=['None']:
            def get_fullName(lid):
                name = user_db[user_db.login_id == np.int64(lid)][['fName', 'lName']]
                return lid, name.fName.tolist()[0] + ' ' + name.lName.tolist()[0]
            for i in event_attendees:
                event_attendees_name.append(get_fullName(i))
        return render_template('view_attendees.html', val=event_attendees_name, event=event)
    else:
        return render_template('method_not_allowed.html')

#update profile page route
@app.route('/edit_profile')
def edit_profile():
    if 'lid' in session:
        return render_template('update_profile.html')
    else:
        return render_template('method_not_allowed.html')

#change password page route
@app.route('/change_pswd')
def change_pswd():
    if 'lid' in session:
        return render_template('change_password.html')
    else:
        return render_template('method_not_allowed.html')

#change dp page route
@app.route('/change_dp')
def change_dp():
    if 'lid' in session:
        return render_template('change_dp.html')
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
    if 'lid' in session:
        session.clear()
        return '''<script>window.location='/'</script>'''
    else:
        return render_template('method_not_allowed.html')

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
        return '''<script>alert('Sign Up Successful');window.location='/'</script>'''
    else:
        return '''<script>alert('Error');window.location='/sign_up'</script>'''

#event creation function route
@app.route('/event_created', methods = ['post'])
def event_created():
    if 'lid' in session:
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
    else:
            return render_template('method_not_allowed.html')

#register event function route
@app.route('/register_event')
def register_event():
    if 'lid' in session:
        global user_db, event_db
        register_eid = request.args.get('e_id')
        if user_db[user_db.login_id == session['lid']].events_reg.tolist()[0] == 'None':
            user_db.at[user_db.login_id == session['lid'], 'events_reg'] = register_eid
        else:
            user_db.at[user_db.login_id == session['lid'], 'events_reg'] = str(user_db.events_reg[user_db['login_id'] == session['lid']].tolist()[0])+' '+str(register_eid)
        if event_db[event_db.event_id == np.int64(register_eid)].participants_reg.tolist()[0] == 'None':
            event_db.at[event_db.event_id == np.int64(register_eid), 'participants_reg'] = str(session['lid'])
        else:
            event_db.at[event_db.event_id == np.int64(register_eid), 'participants_reg'] = str(event_db.participants_reg[event_db['event_id'] == np.int64(register_eid)].tolist()[0])+' '+str(session['lid'])
        user_db.to_csv('database/user_db.csv', index=False)
        user_db = pd.read_csv('database/user_db.csv')
        event_db.to_csv('database/event_db.csv', index=False)
        event_db = pd.read_csv('database/event_db.csv')
        return '''<script>alert('Registered to Event');window.location='/home'</script>'''
    else:
        return render_template('method_not_allowed.html')

#register event function route
@app.route('/attend_event')
def attend_event():
    if 'lid' in session:
        global user_db, event_db
        attended_eid = request.args.get('e_id')
        my_event = get_my_events_df()
        my_event = my_event[my_event.event_id == np.int64(attended_eid)]
        if my_event.live_status.tolist()[0] != 'Live':
            return '''<script>alert("Event isn't Live yet");window.location='/view_my_event?se_id='''+str(attended_eid)+''''</script>'''
        if attended_eid in user_db[user_db.login_id == session['lid']].events_atnd.tolist()[0].split():
            return '''<script>alert('You already marked attendance for this event');window.location='/view_my_event?se_id='''+str(attended_eid)+''''</script>'''
        if user_db[user_db.login_id == session['lid']].events_atnd.tolist()[0] == 'None':
            user_db.at[user_db.login_id == session['lid'], 'events_atnd'] = attended_eid
        else:
            user_db.at[user_db.login_id == session['lid'], 'events_atnd'] = str(user_db.events_atnd[user_db['login_id'] == session['lid']].tolist()[0])+' '+str(attended_eid)
        if event_db[event_db.event_id == np.int64(attended_eid)].participants_atnd.tolist()[0] == 'None':
            event_db.at[event_db.event_id == np.int64(attended_eid), 'participants_atnd'] = str(session['lid'])
        else:
            event_db.at[event_db.event_id == np.int64(attended_eid), 'participants_atnd'] = str(event_db.participants_atnd[event_db['event_id'] == np.int64(attended_eid)].tolist()[0])+' '+str(session['lid'])
        user_db.to_csv('database/user_db.csv', index=False)
        user_db = pd.read_csv('database/user_db.csv')
        event_db.to_csv('database/event_db.csv', index=False)
        event_db = pd.read_csv('database/event_db.csv')
        return '''<script>alert('Marked Attendance');window.location='/view_my_event?se_id='''+str(attended_eid)+''''</script>'''
    else:
        return render_template('method_not_allowed.html')

#cancel registration function route
@app.route('/cancel_event')
def cancel_event():
    if 'lid' in session:
        global user_db, event_db
        cancel_eid = request.args.get('e_id')
        my_event = get_my_events_df()
        my_event = my_event[my_event.event_id == np.int64(cancel_eid)]
        if my_event.live_status.tolist()[0] == 'Live':
            return '''<script>alert('The Event has already started');window.location='/view_my_event?se_id='''+str(cancel_eid)+''''</script>'''
        event_reg_list = user_db[user_db.login_id == session['lid']].events_reg.tolist()[0].split()
        participants_reg_list = event_db[event_db.event_id == np.int64(cancel_eid)].participants_reg.tolist()[0].split()
        event_reg_list.remove(cancel_eid)
        participants_reg_list.remove(str(session['lid']))
        if event_reg_list==[]:
            event_reg_list='None'
        else:
            event_reg_list=' '.join(event_reg_list)
        if participants_reg_list==[]:
            participants_reg_list='None'
        else:
            participants_reg_list=' '.join(participants_reg_list)
        user_db.at[user_db.login_id == session['lid'], 'events_reg'] = event_reg_list
        event_db.at[event_db.event_id == np.int64(cancel_eid), 'participants_reg'] = participants_reg_list
        user_db.to_csv('database/user_db.csv', index=False)
        user_db = pd.read_csv('database/user_db.csv')
        event_db.to_csv('database/event_db.csv', index=False)
        event_db = pd.read_csv('database/event_db.csv')
        return '''<script>alert('Canceled Event Registration');window.location='/my_events'</script>'''
    else:
        return render_template('method_not_allowed.html')

#search event function route
@app.route('/search_event', methods = ['post'])
def search_event():
    if 'lid' in session:
        s_event_name = request.form['search_title']
        if s_event_name.strip() == '':
            return '''<script>alert("Can't Search Empty");window.location='/home'</script>'''
        home_df = get_home_df()
        home_df = home_df[home_df.title == s_event_name]
        if len(home_df)==0:
            return render_template('no_events_found.html')
        return render_template('search_results.html', vals= home_df.sort_values(by='event_id', ascending=False).to_numpy())
    else:
        return render_template('method_not_allowed.html')

#search my event function route
@app.route('/search_my_event', methods = ['post'])
def search_my_event():
    if 'lid' in session:
        s_event_name = request.form['search_title']
        if s_event_name.strip() == '':
            return '''<script>alert("Can't Search Empty");window.location='/my_events'</script>'''
        my_events_df = get_my_events_df()
        my_events_df = my_events_df[my_events_df.title == s_event_name]
        if len(my_events_df)==0:
            return render_template('no_events_found.html')
        return render_template('search_results_mine.html', vals= my_events_df.sort_values(by='date_time', ascending=True).to_numpy())
    else:
        return render_template('method_not_allowed.html')

#update profile function route
@app.route('/update_profile', methods = ['post'])
def update_profile():
    if 'lid' in session:
        global user_db
        update_fname = request.form['update-fname']
        update_lname = request.form['update-lname']
        update_email = request.form['update-email']
        update_phone = request.form['update-phone']
        user_db.at[user_db.login_id == session['lid'], 'fName'] = update_fname
        user_db.at[user_db.login_id == session['lid'], 'lName'] = update_lname
        user_db.at[user_db.login_id == session['lid'], 'email'] = update_email
        user_db.at[user_db.login_id == session['lid'], 'phone'] = update_phone
        user_db.to_csv('database/user_db.csv', index=False)
        user_db = pd.read_csv('database/user_db.csv')
        return '''<script>window.location='/profile'</script>'''
    else:
        return render_template('method_not_allowed.html')

#update profile function route
@app.route('/update_password', methods = ['post'])
def update_password():
    if 'lid' in session:
        global user_db
        update_pswd1 = request.form['update-pswd-1']
        update_pswd2 = request.form['update-pswd-2']
        update_pswd3 = request.form['update-pswd-3']
        if str(user_db[user_db.login_id == session['lid']].password.tolist()[0]) != update_pswd1:
            return '''<script>alert('Incorrect Password');window.location='/change_pswd'</script>'''
        if update_pswd2!=update_pswd3:
            return '''<script>alert('Passwords not Matching');window.location='/change_pswd'</script>'''
        if update_pswd1 == update_pswd2:
            return '''<script>alert("New Password can't be Old Password");window.location='/change_pswd'</script>'''
        user_db.at[user_db.login_id == session['lid'], 'password'] = update_pswd2
        user_db.to_csv('database/user_db.csv', index=False)
        user_db = pd.read_csv('database/user_db.csv')
        return '''<script>alert('Password Changed Login to continue');window.location='/logout'</script>'''
    else:
        return render_template('method_not_allowed.html')

#update dp function route
@app.route('/update_dp', methods=['post'])
def update_dp():
    if 'lid' in session:
        global user_db
        update_dp_img = request.files['update-dp']
        time = datetime.now().strftime('%Y%m%d%H%M%S')
        update_dp_img_name = str(session['lid']) + time
        update_dp_img.save(os.path.join('static/images/profile_pictures', update_dp_img_name+'.png'))
        user_db.at[user_db.login_id == session['lid'], 'profile_pic'] = update_dp_img_name
        user_db.to_csv('database/user_db.csv', index=False)
        user_db = pd.read_csv('database/user_db.csv')
        return '''<script>window.location='/profile'</script>'''
    else:
        return render_template('method_not_allowed.html')

#handling error 404
@app.errorhandler(404)
def error_404(e):
    return render_template('page_not_found.html')

#handling error 405
@app.errorhandler(405)
def error_405(e):
    return render_template('method_not_allowed.html')

if __name__ == '__main__':
    app.run(debug=True)
