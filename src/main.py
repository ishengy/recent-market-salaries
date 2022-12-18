#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 02:17:06 2022

@author: isheng
"""

import os
import linkedin_job_search as ljs
import col_adjustments as ca
from dotenv import load_dotenv
load_dotenv()


def main():

    email = os.environ.get('email')
    password = os.environ.get('password')
    api = ljs.linkedin_job_search(email, password)

    # GET a profile
    days = 45
    job_searches = api.search_jobs(
        job_title= ['25190'], #Senior DS: 25887
        location_name = 'New York City Metropolitan Area',
        listed_at = 24 * 60 * 60 * days,
    )
    num_jobs = len(job_searches)
    print(num_jobs, "jobs found. Approximately", num_jobs*3.5, "seconds to extract job descriptions.")

    job_desc_list = api.get_linkedin_job_desc(job_searches)
    flattened_salaries = api.extract_salaries(job_desc_list)

    salaries_no_outliers = api.tukeys_fences(flattened_salaries)
    salaries_no_outliers.plot.hist(alpha=0.5)

    resampled_means = api.bootstrap_resample(salaries_no_outliers)
    bootstrapped_salaries = salaries_no_outliers.append(resampled_means,ignore_index = True)

    col_table = ca.col_adjustments()
    col_table.update_COL_table()
    adj_factor = col_table.calc_COL_adjustment(city='San Francisco, CA, United States', rent=True)

    bootstrapped_salaries *= adj_factor

    bootstrapped_salaries.plot.hist(alpha=0.5, title = 'NYC DS Salary Distribution (Source: LinkedIn)')


if __name__ == "__main__":
    main()
