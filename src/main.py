#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 02:17:06 2022

@author: isheng
"""

import os
import pandas as pd
import linkedin_job_search as ljs
from dotenv import load_dotenv
load_dotenv()


def append_to_csv(job_title, job_title_code, mu, sigma):
    new_dict = dict(job_title = job_title, job_title_code = int(job_title_code), avg = mu, std_dev = sigma)
    new_data = pd.DataFrame(new_dict, index=[0])

    try:
        curr_data = pd.read_csv('data/job_dist_parameters.csv')
        print('Updating Primary DB')
        updated_data = pd.concat([curr_data, new_data]).reset_index(drop=True)
        updated_data.drop_duplicates(subset = 'job_title_code', keep='last', inplace=True)
        updated_data.to_csv('data/job_dist_parameters.csv', index=False, mode='w')
    except FileNotFoundError:
        print('Primary DB location does not exist. Creating now.')
        new_data.to_csv('data/job_dist_parameters.csv', index=False)
    return True


def main(job_title_code):
    email = os.environ.get('email')
    password = os.environ.get('password')
    api = ljs.linkedin_job_search(email, password)
    df, common_title = api.build_distribution(job_title_code=job_title_code, days=2)
    mu, sigma = df.mean(), df.std()
    append_to_csv(common_title, job_title_code, mu, sigma)


if __name__ == "__main__":
    main('25190')
