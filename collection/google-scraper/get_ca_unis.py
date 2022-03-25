# -*- coding: utf-8 -*-
import pandas as pd

# Import Canadian university list, since they do not use .edu
__ca_unis_file__ = '../../data/metadata/canadian_heis.csv'

list_of_ca_unis = pd.read_csv(__ca_unis_file__, delimiter=',')

cau = list_of_ca_unis['clean_url'].to_list()

for c in cau:
  print(c)