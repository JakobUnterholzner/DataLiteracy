import sys
sys.path.append('..')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from typing import Union

from matplotlib import ticker
import numpy as np
import json
import country_converter as coco
from datetime import datetime, timedelta
import requests
import pandas as pd
import geopandas as gpd
import scipy.stats as sps
import src.geofunctions as gf
import matplotlib.cm as cm



data, Data, population = gf.prepare_datasets(
    '../../dat/tele_and_gov_data.csv',
    '../../dat/surveillance_data.xlsx',
    '../../dat/12411-0010-DLAND_population.csv'
)

geo_df = gf.load_gdp_data('../../dat/ne_10m_admin_1_states_provinces/DE_shapes.csv')
geo_data = geo_df.merge(data, on = 'state')
geo_data['cases_6'] = geo_data.cases_6.apply(lambda x: 1 if x == 0 else x)
geo_data['laws_per_order'] = geo_data.cases_6 / geo_data.cases_4

states_low_lpo = geo_data.query('year==2021 and laws_per_order < 1.05')[['state', 'laws_per_order']] 
ok_states = [s for s in states_low_lpo.state]

ok_population = population.merge(states_low_lpo, on='state').query('year==2021')
ok_population['alpha'] = np.power(ok_population.population / ok_population.population.max(), 1/2)

data_2021 = Data['2021_surveillance']
data_2021 = data_2021.query('paragraph==6')[['description_en']+ok_states]
data_2021['overall'] = data_2021[ok_states].T.sum()
data_2021 = data_2021.sort_values('overall')
data_2021['overall_p'] = data_2021.overall / data_2021.overall.sum()
data_2021['crime'] = data_2021.description_en
data_2021.loc[data_2021.overall_p < 0.05, 'crime'] = 'other'
data_2021.sort_values('overall')
data_2021 = data_2021.groupby('crime').sum()
data_2021 = pd.concat((data_2021.query('crime!="other"').sort_values('overall', ascending=False), data_2021.query('crime=="other"')))

rc_params= {
    # # 'text.usetex': True,
    'font.family': 'serif',
    'font.serif': ['Times'],
    'figure.figsize': (3.25, 2.0086104634371584),
    'figure.constrained_layout.use': True,
    'figure.autolayout': False,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.015,
    'font.size': 8,
    'axes.labelsize': 9,
    'legend.fontsize': 7,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'axes.titlesize': 8
    }
plt.rcParams.update(rc_params)

fig, ax = plt.subplots()
x = np.arange(len(data_2021)+1)
color_list = ['cornflowerblue', 'burlywood', 'coral', 'cadetblue', 'darkgoldenrod'] 
color_list = cm.cubehelix_r(np.linspace(0.2, 0.8, len(color_list)))
step = 1/6
for i, s in enumerate(ok_population.sort_values('population').tail(5).state):
    y = list(data_2021[s]/data_2021[s].sum())
    ax.bar(x[:-1] + step*(i +1), y, color=color_list[i], label = s, width = 1/6)

    # ax.step(x, [y[0]] + y, label=s)
base = list(data_2021.overall_p)
ax.step(x, [base[0]] + base, c='black', ls='--', label='base', lw=1)
plt.xlim(-0.1, 6 + 0.1)
ax.set_ylim(0.,0.5)
ax.set_ylabel('$P(c|s)$')
ax.legend()
ax.grid(axis='y')
ax.set_axisbelow(True)
ax.set_xticks(x[1:]-.5, ['Narcotics', 'Fraud', 'Gang theft', 'Murder', 'Robbery', 'other'], rotation=0)
plt.savefig('crime_dist.pdf')


def plot_map_new(
        geo_df: pd.DataFrame, 
        columns: str, 
        title: str = None, 
        dst_path: str = None,
        cmap: str = 'Blues'):
    """
    Plot german map with colorbar.
    
    arguments:
    geo_df -- data prepared with `data_to_geo`
    column -- value which is used to indicate levels across states, e.g. 'cases_3_per_1k'
    title -- plot titile
    dst_path -- if provided save figure, e.g. './map_rel_2021.png'
    cmap -- colormap for the plot

    returns:
    fig, ax - tuple of matplotlib Figure and Axes
    """
    fig, axes = plt.subplots(1,2, figsize=(11.5, 6 ))
    cmap = ['Blues', 'Purples']

    

    for i, column, ax in zip(range(2), columns, axes):
        ax = geo_df.plot(column=column, ax=ax, edgecolor='0.8', linewidth=1, cmap=cmap[i])
        ax.set_title(title, fontdict={'fontsize': '16', 'fontweight': '3'})

        for idx, row in geo_df.iterrows():
            x = row['coords'][0] - 0.1
            y = row['coords'][1]
            text = ax.annotate(
                text=f"{row['state']}",
                xy=(x,y),
                xytext= (x,y), 
                fontsize=16,
                color='black',
            )
            text.set_path_effects([path_effects.Stroke(linewidth=1, foreground='white'),
                                path_effects.Normal()])

        # ax.axis('off')
        ax.set_xlim(5.5, 15.4)
        ax.set_ylim(47.1, 55.3)
        ax.set_xticks([])
        ax.set_yticks([])

        vmin, vmax = geo_df[column].min(), geo_df[column].max()
        sm = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=vmin, vmax=vmax), cmap=cmap[i])
        step = [0.435, 0.935]
        cbaxes = fig.add_axes([step[i]+0.02, 0.015, 0.02, 1.-0.09])
        cbar = fig.colorbar(sm, cax=cbaxes)
        cbaxes.tick_params(labelsize=20)
        label = ['$P(s)$, %', 'LPO']
        cbaxes.annotate(label[i], (-3,404), color='black', xycoords='axes points', fontsize=20)

    if dst_path:
        plt.savefig(dst_path, dpi=400)

    return fig, ax

geo_data['case_4_proba_100'] = geo_data.case_4_proba*100
plot_map_new(geo_data.query('year==2021'), ['case_4_proba_100', 'laws_per_order'], dst_path='maps.pdf')


