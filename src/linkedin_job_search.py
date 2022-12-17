#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 02:17:06 2022

@author: isheng
"""

from linkedin_api import Linkedin
import pandas as pd
import re
import time
import numpy as np


class linkedin_job_search(Linkedin):

    def find_salary(self, text):
        return re.findall(r'\$\d{2,3}\,\d{3}', text)

    def flatten(self, big_list):
        return [int(item.replace("$","").replace(",","")) for sublist in big_list for item in sublist]

    def tukeys_fences(self, arr):
        q1 = np.quantile(arr, 0.25)
        q3 = np.quantile(arr, 0.75)
        iqr = q3 - q1

        upper_bound = q3+(1.5*iqr)
        lower_bound = q1-(1.5*iqr)

        return arr[(arr >= lower_bound) & (arr <= upper_bound)]

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

    def extract_salaries(self, job_desc_list):
        salaries = [self.find_salary(job_text) for job_text in job_desc_list if len(self.find_salary(job_text)) > 0]
        return pd.Series(self.flatten(salaries), name = 'salaries')

    def bootstrap_resample(self, arr):
        resampled_means = pd.Series([arr.sample(3).mean() for i in range(0,1000)], name = 'salaries')
        bootstrapped_salaries = arr.append(resampled_means,ignore_index = True)
        return bootstrapped_salaries
