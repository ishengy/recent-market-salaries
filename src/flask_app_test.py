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
from math import ceil
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['TESTING'] = True

@app.route('/')
def hello():
    test_df = pd.read_csv('data/job_dist_parameters.csv')
    return render_template('index.html', job_list=test_df.job_title,)


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


get_plot = False


@app.route('/get_plot', methods=['GET', 'POST'])
def get_plot():
    test_df = pd.read_csv('data/job_dist_parameters.csv')
    if request.method == 'POST':
        test_df = pd.read_csv('data/job_dist_parameters.csv')

        location = request.form['geo_loc']
        curr_salary = request.form['curr_salary']
        job_titles = request.form['job']
        print(location)
        print(job_titles)

        data_row = test_df[test_df.job_title == job_titles]

        mu = data_row.avg.values[0]
        sigma = data_row.std_dev.values[0]

        # if not norm - replace bottom with skewnorm
        if data_row.normal_dist.values[0]:
            x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
            fill_x = np.arange(min(x), int(curr_salary), 10)
            percentile = stats.norm(mu, sigma).cdf(int(curr_salary))
            plt.plot(x, stats.norm.pdf(x, mu, sigma))
            fill_y = stats.norm.pdf(fill_x, mu, sigma)
        else:
            # this doesnt work for skewnorm - figure something out lmao
            x = np.linspace(mu - 1.5*sigma, mu + 3.5*sigma, 100)
            fill_x = np.arange(min(x), int(curr_salary), 10)
            ae = data_row['shape'].values[0]
            percentile = stats.skewnorm(ae, mu, sigma).cdf(int(curr_salary))
            plt.plot(x, stats.skewnorm.pdf(x, ae, mu, sigma))
            fill_y = stats.skewnorm.pdf(fill_x, ae, mu, sigma)

        plt.fill_between(fill_x, fill_y, color='g')
        plt.title('Salary Distribution (Source: LinkedIn)')
        plt.ylabel('Density')
        plt.xlabel('Salary')
        plt.savefig('static/my_plot.png')
        plt.close()

        output_mean = ('The mean salary is $' + str(round(mu)))
        output_std = ('The standard deviation is $' + str(round(sigma)))
        output_compare = ('This means that your salary falls in the ' + str(ceil(percentile*100)) + 'th percentile.')
        return render_template(
            'index.html',
            get_plot=True,
            plot_url='static/my_plot.png',
            job_list=test_df.job_title,
            output_mean=output_mean,
            output_std=output_std,
            output_compare=output_compare,
        )
    else:
        return render_template('index.html', job_list=test_df.job_title,)


app.secret_key = 'Stophackingme!'

#Run the app on localhost port 5000
if __name__ == "__main__":
    app.run('0.0.0.0', 5000, debug = True)