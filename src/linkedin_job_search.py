#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 02:17:06 2022

@author: isheng
"""

from linkedin_api import Linkedin
import col_adjustments as ca
import pandas as pd
import re
import time
import numpy as np
import scipy.stats as stats


class linkedin_job_search(Linkedin):

    def find_salary(self, text):
        return re.findall(r'\$\d{2,3}\,\d{3}', text)

    def flatten(self, big_list):
        return [int(item.replace("$","").replace(",","")) for sublist in big_list for item in sublist]

    def outlier_removal(self, arr, how='tukey'):
        if how == 'tukey':
            q1 = np.quantile(arr, 0.25)
            q3 = np.quantile(arr, 0.75)
            iqr = q3 - q1

            upper_bound = q3+(1.5*iqr)
            lower_bound = q1-(1.5*iqr)

            removed = arr[(arr >= lower_bound) & (arr <= upper_bound)]
        elif how == 'z-score':
            mean, std = np.mean(arr), np.std(arr)
            z_score = np.abs((arr - mean) / std)
            removed = arr[z_score < 2]
        elif how == 'modified-z':
            mad = abs(arr - arr.median()).sum()/len(arr)
            m = 0.6745 * (arr - np.median(arr)) / mad
            removed = arr[abs(m) < 3.5]
        return removed

    def get_linkedin_job_desc(self, job_searches):
        job_desc_list = []
        i = 0
        cum_time = 0
        for job in job_searches:
            t0 = time.time()
            i += 1
            delimited = job['entityUrn'].split(':')
            job_id = delimited[len(delimited) - 1]
            job_desc_list.append(self.get_job(job_id)['description']['text'])
            cum_time += (time.time() - t0)
            print(i, "Elapsed Time:", cum_time)

        return job_desc_list

    def extract_salaries(self, job_desc_list, exempt=True):
        salaries = [self.find_salary(job_text) for job_text in job_desc_list if len(self.find_salary(job_text)) > 0]
        flattened_salaries = pd.Series(self.flatten(salaries), name = 'salaries')

        if exempt:
            flattened_salaries = flattened_salaries[flattened_salaries >= 58500]

        return flattened_salaries

    def bootstrap_resample(self, arr):
        resampled_means = pd.Series([arr.sample(3).mean() for i in range(0,1000)], name = 'salaries')
        bootstrapped_salaries = arr.append(resampled_means,ignore_index = True)
        return bootstrapped_salaries

    def test_normality(self, observed_data, alpha = 1e-3):
        chi_square_test_statistic, p_value = stats.normaltest(observed_data)
        if p_value < alpha:  # null hypothesis: x comes from a normal distribution
            print("The null hypothesis can be rejected")
        else:
            print("The null hypothesis cannot be rejected")

    def build_distribution(self, job_title_code, days, use_normal=False, bootstrap=True, update_table=False, col_adj_city='New York, NY, United States', col_with_rent=True):

        # GET a profile
        print('Gathering Job Postings')
        job_searches = self.search_jobs(
            job_title = [job_title_code],
            job_type=['F'],
            location_name = 'New York City Metropolitan Area',
            listed_at = 24 * 60 * 60 * days,
        )
        num_jobs = len(job_searches)
        print(num_jobs, "jobs found. Approximately", num_jobs*3.5, "seconds to extract job descriptions.")

        job_desc_list = self.get_linkedin_job_desc(job_searches)
        flattened_salaries = self.extract_salaries(job_desc_list)

        # if normal, maybe just grab mean+std and build out normal distribution.
        # if not, bootstrap?
        # self.test_normality(flattened_salaries)

        salaries_no_outliers = self.outlier_removal(flattened_salaries, how='tukey')
        salaries_no_outliers.plot.hist(alpha=0.5)

        if bootstrap:
            print('Bootstrapping')
            try:
                resampled_means = self.bootstrap_resample(salaries_no_outliers)
                salaries_no_outliers = salaries_no_outliers.append(resampled_means,ignore_index = True)
            except ValueError:
                print('Not enough salaries to initiate bootstrap. Try increasing the number of days.')

        if col_adj_city != 'New York, NY, United States':
            col_table = ca.col_adjustments()
            if update_table:
                print('Updating Table')
                col_table.update_COL_table()
            print('Adjusting for COL')
            adj_factor = col_table.calc_COL_adjustment(city=col_adj_city, rent=col_with_rent)
            salaries_no_outliers *= adj_factor

        print('Creating Visuals')
        salaries_no_outliers.plot.hist(alpha=0.5, title = 'Salary Distribution (Source: LinkedIn)')

        return True
