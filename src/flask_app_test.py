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
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['TESTING'] = True

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
        percentile = stats.norm(mu, sigma).cdf(int(curr_salary))
        z = stats.norm.ppf(percentile)

        x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
        plt.plot(x, stats.norm.pdf(x, mu, sigma))

        fill_x = np.arange(x[0], int(curr_salary), 10)
        fill_y = stats.norm.pdf(fill_x, mu, sigma)

        plt.fill_between(fill_x, fill_y, color='r')
        plt.savefig('static/my_plot1.png')
        plt.close()

        output_mean = ('The mean salary is $' + str(mu))
        output_std = ('The standard deviation is $' + str(sigma))
        output_compare = ('This means that your salary falls in the ' + str(round(percentile*100, 2)) + 'th percentile.')
        # browser caching issues. idea to fix: append an incrementer like my_plot4.png. delete previous incremented file, increment counter, create new my_plot5.png file.
        # or ... plotly?
        return render_template('index.html', get_plot = True, plot_url = 'static/my_plot1.png', output_mean=output_mean, output_std=output_std, output_compare=output_compare)
    else:
        return render_template('index.html')


app.secret_key = 'Stophackingme!'

#Run the app on localhost port 5000
if __name__ == "__main__":
    app.run('0.0.0.0', 5000, debug = True)