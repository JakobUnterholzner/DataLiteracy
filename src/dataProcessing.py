'''
This file contains functions for data processing.
@Autor: Jakob Unterholzner
'''

import numpy as np
import pandas as pd

def yearlySum(xls):
    '''
    This function sums up the data of each year and returns a dataframe with the summed up data.
    '''
    # Get the names of all sheets in the Excel file
    sheet_names = xls.sheet_names

    # Read each sheet into a separate DataFrame and store them in a list
    dfs = [pd.read_excel(xls, sheet_name) for sheet_name in sheet_names]

    # Add a 'Year' column to each DataFrame
    for i in range(len(dfs)):
        dfs[i]['Year'] = sheet_names[i].replace('_surveillance', '')
    
    # Concatenate all DataFrames into one
    data = pd.concat(dfs, ignore_index=True)

    # Convert the 'Year' column to datetime index
    data['Year'] = data['Year'].astype(int)
    data['Year'] = pd.to_datetime(data['Year'], format='%Y')
    data.set_index('Year', inplace=True)

    #We only analyse pargraph 6 as these are the actual crimes
    data_paragraph6 = data[data['paragraph'].isin([1,6])]
    data_paragraph6_int = data_paragraph6.select_dtypes(include=['int'])
    data_yearly = data_paragraph6_int.groupby('Year').sum()
    data_yearly = data_yearly.drop(['GBA', 'overall', 'paragraph'], axis=1)
    
    return data_yearly