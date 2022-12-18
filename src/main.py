#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 02:17:06 2022

@author: isheng
"""

import os
import col_adjustments as ca
import linkedin_job_search as ljs
from dotenv import load_dotenv
load_dotenv()


def main():
    email = os.environ.get('email')
    password = os.environ.get('password')
    api = ljs.linkedin_job_search(email, password)
    test = api.build_distribution(job_title_code='757', days=45)


if __name__ == "__main__":
    main()
