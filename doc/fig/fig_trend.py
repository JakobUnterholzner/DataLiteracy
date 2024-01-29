'''This scirpt creates a figures (PDF), which is stored in the
same fig directory.
@author: Jakob Unterholzner
'''

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from tueplots import bundles
from matplotlib.patches import Patch


###################################################################################################
#1. Prepare the surveillance data
xlsx = pd.ExcelFile('dat/surveillance_data.xlsx')
sheet_names = xlsx.sheet_names
dfs = [pd.read_excel(xlsx, sheet_name) for sheet_name in sheet_names]

# Add a 'Year' column to each DataFrame
for i in range(len(dfs)):
    dfs[i]['Year'] = sheet_names[i].replace('_surveillance', '')
 
# Concatenate all DataFrames into one
surv = pd.concat(dfs, ignore_index=True)

# Formatting
surv['Year'] = pd.to_datetime(surv['Year'].astype(int), format='%Y')
surv.set_index('Year', inplace=True)


#We only analyse pargraph 4 as these are the actual surveillance Orders
surv = surv[surv['paragraph'].isin([4])]
surv.drop(['description', 'description_en', 'overall','paragraph', 'GBA'], axis=1, inplace=True)
surv['mean'] = surv.mean(axis=1, numeric_only=True).round().astype(int)

###################################################################################################
#2. Prepare the population data
population = pd.read_csv('dat/12411-0010-DLAND_$F.csv',
                        sep=';', skiprows=5, skipfooter=4, engine='python')
population['state'] = ['BW', 'BY', 'BE', 'BB', 'HB', 'HH', 'HE', 'MV', 'NI',\
                       'NW', 'RP', 'SL', 'SN', 'ST', 'SH', 'TH']
population.drop(['Unnamed: 0'], axis=1, inplace=True)
population.columns = population.columns.str.replace('31.12.', '')
population = pd.melt(population, id_vars=['state'], value_vars=population.columns[1:])
population.columns = ['state', 'year', 'population']
population['year'] = population.year.astype('int64')

###################################################################################################
#3. Combine data
surv = surv.reset_index().melt(id_vars='Year', var_name='state', value_name='count')
surv['year'] = pd.to_datetime(surv['Year']).dt.year

# Merge data_yearly_melted and population
merged_df = pd.merge(surv, population, how='inner', on=['state', 'year'])

# Every second row contain prolonged orders, so we shift the data by one row
merged_df['count4.2'] = merged_df['count'].shift(-1)
merged_df = merged_df.iloc[::2]

#Calculate the sum over states for a germnay wide surveillance order number
# Group the data by year and calculate the sum of counts and population
ger_data = merged_df.groupby('year').agg({'count': 'sum', 'count4.2': 'sum', 'population': 'sum'}).reset_index()
ger_data['state'] = 'GER'
merged_df = pd.concat([merged_df, ger_data], ignore_index=True)

merged_df['count'] = merged_df['count'].astype(int)
merged_df['count4.2'] = merged_df['count4.2'].astype(int)
merged_df['count_sum'] = merged_df['count'] + merged_df['count4.2']

#divide count by population & scale by 100.000
merged_df['count_norm'] = (merged_df['count'] / merged_df['population'] * 100_000).round(5)
merged_df['count4.2_norm'] = (merged_df['count4.2'] / merged_df['population'] * 100_000).round(5)
merged_df['count_sum_norm'] = (merged_df['count_sum'] / merged_df['population'] * 100_000).round(5)

# Sort the DataFrame to have the states ordered by population
merged_df.sort_values(by='population', ascending=False, inplace=True)
states_by_pop = merged_df['state'].unique()

#transform to wide format
count_sum_norm = merged_df.pivot(index='state', columns='year', values='count_sum_norm')

# Convert the index to a categorical type with the states ordered by 'states_by_pop'
count_sum_norm.index = pd.Categorical(count_sum_norm.index, categories=states_by_pop, ordered=True)
count_sum_norm.sort_index(inplace=True)
count_sum_norm.drop('GER', inplace=True)




###################################################################################################
# 4. Plotting
plt.rcParams.update(bundles.icml2022(column="full", nrows=1, ncols=1, usetex=False))
fig, ax = plt.subplots(1,1)

# Create a list of x coordinates for the bars
x = range(len(count_sum_norm.index))
bar_width = 0.065

# Create a color map
colors = cm.cubehelix_r(np.linspace(0.2, 0.8, len(count_sum_norm.columns)))
legend_patches = []

# Create a bar plot for each column
for i, (year, color) in enumerate(zip(count_sum_norm.columns, colors)):
    ax.bar([xi*(1+bar_width) + i*bar_width for xi in x], count_sum_norm[year],
           width=bar_width, label=year, color=color)
    legend_patches.append(Patch(color=color, label=year))

# Set the labels of the x-axis, y-axis and title
ax.set_xlabel('Federal States of Germany (sorted by population)')
ax.set_ylabel('Surv. Orders per 100.000 Inhabitants')

# Set the x-ticks to be the states and rotate them
plt.xticks([xi*(1+bar_width) + 0.5*len(count_sum_norm.columns)*bar_width for xi in x], 
           count_sum_norm.index, rotation=0)
ax.grid(which="major", axis="y", alpha=0.5)
# Set the x-axis limits
ax.set_xlim(x[0]*(1+bar_width) - 0.5*bar_width,
            x[-1]*(1+bar_width) + (len(count_sum_norm.columns)+0.5)*bar_width)
ax.set_axisbelow(True)

# Display the legend
ax.legend(handles=legend_patches, loc="upper left", framealpha=1, facecolor="white", ncol=2)
plt.savefig('doc/fig/trend.pdf')
plt.show()

