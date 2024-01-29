import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from tueplots import bundles
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

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
surv.drop(['description', 'description_en', 'overall','paragraph'], axis=1, inplace=True)
surv['sum'] = surv.iloc[:, 1:].sum(axis=1, numeric_only=True).round().astype(int)

# Every second row contain prolonged orders, so we shift the data by one row
surv['sum4.2'] = surv['sum'].shift(-1)
surv = surv.iloc[::2]

# Create a DataFrame with only the data for Germany for later use
ger_data = surv[['sum', 'sum4.2']].copy()
ger_data.index = pd.to_datetime(ger_data.index, format='%Y')

# Shift the dates to the last day of the year for plotting
ger_data.index = ger_data.index + pd.offsets.YearEnd(1)
ger_data.sort_index(inplace=True)

##################################################################################################
# 2. Mobile user data
mobile_data = pd.read_csv('dat/mobile_user_germany.csv', sep=';', header=0)

# Select rows where 'Jahr' is between 2008 and 2021 and create a copy
mobile_data = mobile_data[mobile_data['Jahr'].between(2008, 2021)].copy()
mobile_data = mobile_data[mobile_data['Quartal'].isin([4])]
mobile_data['Quartal'] = mobile_data['Quartal'].astype(int) 
mobile_data['Date'] = pd.to_datetime(mobile_data['Jahr'].astype(str) + '-' + '12' + '-31')
mobile_data.set_index('Date', inplace=True)
mobile_data.drop(['Jahr', 'Quartal'], axis=1, inplace=True)


##################################################################################################
# 3. Plotting

plt.rcParams.update(bundles.icml2022(column="half", nrows=1, ncols=1, usetex=False))
fig, ax = plt.subplots(1,1)

colors = cm.cubehelix_r(np.linspace(0.2, 0.8, 5))
base = ax.bar(ger_data.index.year, ger_data['sum4.2'],
              color=colors[3], label='prolonged')
top = ax.bar(ger_data.index.year, ger_data['sum'],
             bottom=ger_data['sum4.2'], color=colors[2], label='initial')

#406d2a
#b9c3f2
ax2 = ax.twinx()
user = ax2.plot(mobile_data.index.year, mobile_data['Gesamt'], linestyle='dashed',
                 color='black', linewidth=1, label='mobile users')


# Set the labels of the x-axis, y-axis and title
ax.set_ylabel('Surv. Orders')
ax2.set_ylabel('User in 100 Mio.')

# Set the x-ticks to be the states and rotate them
labels = ['' if i % 2 else str(year) for i, year in enumerate(ger_data.index.year)]
plt.xticks(ger_data.index.year, labels, rotation=0)
ax.grid(which="major", axis="y", alpha=0.5)

# ask matplotlib for the plotted objects and their labels
lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc="upper center" ,
           framealpha=1, facecolor="white", ncol=3)
ax.set_ylim([0,27500])

plt.savefig('doc/fig/trend_and_user.pdf')
plt.show()