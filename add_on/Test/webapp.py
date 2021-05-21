from flask import *
import os
import pandas as pd
import numpy as np

app = Flask(__name__)
app.secret_key = 'xyz'

@app.route("/")
def main():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()