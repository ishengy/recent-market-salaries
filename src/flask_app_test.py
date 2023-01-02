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
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json

import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

@app.route('/')
def hello():
    test_df = pd.read_csv('data/job_dist_parameters.csv')
    col_adj = pd.read_csv('data/numbeo_col.csv')
    return render_template('landing.html', job_list=test_df.job_title.unique(), loc_list = col_adj.City)


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
    col_adj = pd.read_csv('data/numbeo_col.csv')
    test_df = pd.read_csv('data/job_dist_parameters.csv')

    exp_conversion = pd.DataFrame.from_dict({
        'experience': ['-1', '2, 3', '4', '5', '6'],
        'exp_title': ['All Experiences', 'Entry + Associate', 'Mid-Senior', 'Director', 'Executive'],
    })
    state = False

    if request.method == 'POST':

        location = request.form['geo_loc']
        curr_salary = request.form['curr_salary']
        job_titles = request.form['job']

        job_rows = test_df[(test_df.job_title == job_titles)].sort_values('experience')
        job_rows = pd.merge(job_rows, exp_conversion, how='inner', on='experience')
        print(job_titles)

        # error here. if there is already a selection, and you change to diff job then that doesnt have exp then error
        # ex: data scientist @ 'Entry + Associate' levels -> select media planner (it doesnt have entry + ass) -> error out
        # fix - maybe change state after first select?
        # initial state = False, after pressing submit set state = True?
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
            norm_warning = 'The distribution is not normal, so take the following with a grain of salt:'

        plt.fill_between(fill_x, fill_y, color='g')
        plt.title('Salary Distribution (Source: LinkedIn)')
        plt.ylabel('Density')
        plt.xlabel('Salary')
        plt.savefig('static/images/my_plot.png')
        plt.close()

        output_mean = ('The mean salary is $' + str(round(mu)))
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


@app.route('/chart1')
def chart1():
    df = pd.DataFrame({
        "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
        "Amount": [4, 1, 2, 2, 4, 5],
        "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    })

    fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

    """
    refer to get_plot(), but this hsould be how we can build the dist
    fig = px.line(x=x, y=stats.norm.pdf(x, mu, sigma), title='Life expectancy in Canada')
    fig.add_trace(go.Scatter(
        x=fill_x,
        y=fill_y,
        fill='tozeroy',
        fillcolor='rgba(0,100,80,0.2)',
        line_color='rgba(255,255,255,0)',
        showlegend=False,
        name='Fair',
    ))
    add filter to above

    OR

    just create new html, new url redirect, and render the new html that contains button or dropdown menus 
    of differing experience levels instead of this dynamic headache shit lmao. might be easier to do this one:

    @app.route('/job-exp-plots', methods=['GET', 'POST'])
    [RETAIN FORM HTML SO IT LOOKS LIKE THE PAGE DIDNT CHANGE LOL]
    after pressing submit, it should lead us to the next page that retains 
    the same form, but with a new dropdown menu for the experiences.
    the rest will function the same
    add new html code below:
    exp1, exp2, exp3 -> Submit
    render graph of either 1 2 or 3
    """

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Fruit in North America"
    description = """
    A academic study of the number of apples, oranges and bananas in the cities of
    San Francisco and Montreal would probably not come up with this chart.
    """
    return render_template('notdash2.html', graphJSON=graphJSON, header=header,description=description)


app.secret_key = 'some key that you will never guess'

#Run the app on localhost port 5000
if __name__ == "__main__":
    # app.run('0.0.0.0', 5000, debug = True)
    app.run('127.0.0.1', 5000, debug = True)