#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 02:17:06 2022

@author: isheng
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup


class col_adjustments:

    def __init__(self):
        self.bls_state_salary = pd.read_csv("data/numbeo_col.csv")
        self.cities = self.bls_state_salary.City.unique()

    def update_COL_table(self):
        table_url = "https://www.numbeo.com/cost-of-living/rankings_current.jsp"
        response = requests.get(table_url)
        status_code = response.status_code

        if status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            col_table = soup.find('table',{'class':'stripe'})
            df = pd.read_html(str(col_table))[0].drop(columns = 'Rank')
            df.to_csv("data/numbeo_col.csv")
            msg = "COL Table Updated"
        else:
            msg = "COL Table Not Updated."

        return msg

    def calc_COL_adjustment(self, city, rent=True):
        city_row = self.bls_state_salary[self.bls_state_salary.City == city]
        if rent:
            col = "Cost of Living Plus Rent Index"
        else:
            col = "Cost of Living Index"

        col_city_index = city_row[col].values[0]/100

        return col_city_index
