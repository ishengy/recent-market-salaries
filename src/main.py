#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 02:17:06 2022

@author: isheng
"""

import os
import linkedin_job_search as ljs
from dotenv import load_dotenv
load_dotenv()


def main():
    email = os.environ.get('email')
    password = os.environ.get('password')
    api = ljs.linkedin_job_search(email, password)
    api.build_distribution(job_title_code='25190', days=1)


if __name__ == "__main__":
    main()
