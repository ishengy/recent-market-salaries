#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 02:17:06 2022

@author: isheng
"""

import matplotlib
matplotlib.use('Agg')
import os
from flask import Flask, render_template
from flask import request
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import math
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('index.html')


get_plot = False


@app.route('/get_plot', methods=['GET', 'POST'])
def get_plot():
    test_dict = dict(code = '25190', title = 'Data Scientist', avg = 145000, std_dev = 10000)
    test_df = pd.DataFrame(test_dict, index=[0])
    if request.method == 'POST':
        job_title_code = request.form['job_title_code']
        location = request.form['geo_loc']
        curr_salary = request.form['curr_salary']

        data_row = test_df[test_df.code == job_title_code]
        print(data_row.title.values[0])

        mu = data_row.avg.values[0]
        sigma = data_row.std_dev.values[0]

        x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
        plt.plot(x, stats.norm.pdf(x, mu, sigma))
        plt.savefig('static/my_plot.png')
        return render_template('index.html', get_plot = True, plot_url = 'static/my_plot.png')
    else:
        return render_template('index.html')


app.secret_key = 'Stophackingme!'

#Run the app on localhost port 5000
if __name__ == "__main__":
    app.run('0.0.0.0', 5000, debug = True)