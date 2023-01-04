#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 02:17:06 2022

@author: isheng
"""

from flask import Flask, render_template
from flask import request
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from math import ceil
import pandas as pd

import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

test_df = pd.read_csv('data/job_dist_parameters.csv')
col_adj = pd.read_csv('data/numbeo_col.csv')

@app.route('/')
def hello():
    return render_template('landing.html', job_list=test_df.job_title.unique(), loc_list = col_adj.City)


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to not cache the rendered page.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


get_plot = False


@app.route('/get_plot', methods=['GET', 'POST'])
def get_plot():
    exp_conversion = pd.DataFrame.from_dict({
        'experience': ['-1', '2, 3', '4', '5', '6'],
        'exp_title': ['All Experiences', 'Entry + Associate', 'Mid-Senior', 'Director', 'Executive'],
    })

    if request.method == 'POST':

        location = request.form['geo_loc']
        curr_salary = request.form['curr_salary']
        job_titles = request.form['job']

        job_rows = test_df[(test_df.job_title == job_titles)].sort_values('experience')
        job_rows = pd.merge(job_rows, exp_conversion, how='inner', on='experience')
        print(job_titles)

        try:
            experience = request.form['exp']
        except:
            experience = job_rows.iloc[0].exp_title

        print(experience)
        adj_factor = col_adj[col_adj.City == location]['Cost of Living Index'].values[0]/100
        data_row = job_rows[(job_rows.exp_title == experience)]

        if len(data_row) == 0:
            experience = job_rows.iloc[0].exp_title
            data_row = job_rows[(job_rows.exp_title == experience)]

        mu = data_row.avg.values[0] * adj_factor
        sigma = data_row.std_dev.values[0] * adj_factor

        # if not norm - replace bottom with skewnorm
        if data_row.normal_dist.values[0]:
            summary_stat = 'mean'
            x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
            fill_x = np.arange(min(x), int(curr_salary), 10)
            percentile = stats.norm(mu, sigma).cdf(int(curr_salary))
            y = stats.norm.pdf(x, mu, sigma)
            fill_y = stats.norm.pdf(fill_x, mu, sigma)
            norm_warning = ''
        else:
            # not the best approach
            summary_stat = 'median'
            x = np.linspace(mu - 1.5*sigma, mu + 3.5*sigma, 100)
            fill_x = np.arange(min(x), int(curr_salary), 10)
            ae = data_row['shape'].values[0]
            percentile = stats.skewnorm(ae, mu, sigma).cdf(int(curr_salary))
            y = stats.skewnorm.pdf(x, ae, mu, sigma)
            fill_y = stats.skewnorm.pdf(fill_x, ae, mu, sigma)
            mu = stats.skewnorm(ae, mu, sigma).ppf(0.5)
            norm_warning = 'The distribution is not normal, so take the following with a grain of salt:'

        plt.figure(figsize=(7,5))
        plt.plot(x, y, alpha=0.65)
        plt.fill_between(fill_x, fill_y, alpha=0.2)
        plt.title('Salary Distribution \n (Source: LinkedIn, Sample Size: ' + str(int(data_row.num_salary.values[0])) + ')')
        plt.ylabel('Density')
        plt.xlabel('Salary')
        plt.savefig('static/images/my_plot.png')
        plt.close()

        output_mean = ('The ' + summary_stat + ' salary is $' + str(round(mu)))
        output_std = ('The standard deviation is $' + str(round(sigma)))
        output_compare = ('This means that your salary falls in the ' + str(ceil(percentile*100)) + 'th percentile.')
        non_nyc_warning = ''
        if location != 'New York, NY, United States':
            non_nyc_warning = 'This plot is created by adjusting against NYC Cost of Living; it is not an accurate representation of the salaries in ' + location + '.'

        # need to also add normal warning message
        return render_template(
            'index.html',
            get_plot=True,
            plot_url='static/images/my_plot.png',
            job_list=test_df.job_title.unique(),
            exp_list=job_rows.exp_title,
            output_mean=output_mean,
            output_std=output_std,
            output_compare=output_compare,
            loc_list=col_adj.City,
            selected_job=job_titles,
            selected_loc=location,
            selected_salary=curr_salary,
            selected_exp=experience,
            warning_msg=non_nyc_warning,
            norm_warning=norm_warning,
        )
    else:
        return render_template('index.html', job_list=test_df.job_title.unique(), loc_list=col_adj.City,)


app.secret_key = 'some key that you will never guess'

#Run the app on localhost port 5000
if __name__ == "__main__":
    # app.run('0.0.0.0', 5000, debug = True)
    app.run('127.0.0.1', 5000, debug = True)