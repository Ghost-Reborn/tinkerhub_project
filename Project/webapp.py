### importing libraries
from flask import *
import os
import numpy as np
import pandas as pd

#creating flask object
app = Flask(__name__)
app.secret_key = 'xyz'

@app.route('/')
def main():
    return render_template('login.html')

@app.route('/login', methods = ['post'])
def login():
    login_email = request.form['login_email']
    login_pswd = request.form['login_pswd']
    return '''<script>alert('Logging In');window.location='/'</script>'''

@app.route('/sign_up')
def signing_up():
    return '''<script>alert('Signing Up');window.location='/sign_up'</script>'''

if __name__ == '__main__':
    app.run(debug=True)
