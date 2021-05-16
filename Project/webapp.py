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
    return '''<script>alert('Fail');window.location='/'</script>'''

if __name__ == '__main__':
    app.run(debug=True)