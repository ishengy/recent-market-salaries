#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 02:17:06 2022

@author: isheng
"""

import os
import pandas as pd
import linkedin_salary_tools as ljs
from dotenv import load_dotenv
load_dotenv()


def append_to_csv(job_title, job_title_code, mu, sigma, a, n, norm, experience):
    if experience is None:
        str_exp = '-1'
    else:
        str_exp = ', '.join(experience)

    new_dict = dict(
        job_title = job_title,
        job_title_code = int(job_title_code),
        avg = mu,
        std_dev = sigma,
        shape = a,
        normal_dist = norm,
        num_salary = n,
        experience = str_exp,
    )
    new_data = pd.DataFrame(new_dict, index=[0])

    try:
        curr_data = pd.read_csv('data/job_dist_parameters.csv')
        print('Updating Primary DB')
        updated_data = pd.concat(
            [curr_data, new_data]
        ).reset_index(drop=True)

        updated_data.drop_duplicates(
            subset=['job_title_code', 'experience'],
            keep='last',
            inplace=True
        )

        updated_data = updated_data.sort_values('job_title')

        updated_data.to_csv(
            'data/job_dist_parameters.csv',
            index=False,
            mode='w'
        )
    except FileNotFoundError:
        print('Primary DB location does not exist. Creating now.')
        new_data.to_csv('data/job_dist_parameters.csv', index=False)
    return True


def main(job_title_code, limit=-1, experience=None):
    email = os.environ.get('email')
    password = os.environ.get('password')
    api = ljs.linkedin_job_search(email, password)
    df, common_title, a, mu, sigma, n = api.build_distribution(
        job_title_code=job_title_code,
        days=30,
        limit=limit,
        experience=experience,
    )
    normality = True
    if a != 0:
        normality = False
    append_to_csv(common_title, job_title_code, mu, sigma, a, n, normality, experience)

    return df


if __name__ == "__main__":
    main(
        job_title_code='9',
        limit=450,
        experience=['4'],
    )
    # senior roles: 10331, 7797,
    # non senior: 25201, 3114, 58
