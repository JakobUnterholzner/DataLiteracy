import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from typing import Union
from shapely.wkt import loads

import numpy as np
import pandas as pd
import geopandas as gpd
import scipy.stats as sps


def prepare_datasets(
        party_data_path: str,
        surveillance_data: str,
        population_data_path: str,
        ) -> tuple[pd.DataFrame, ...]:
    """
    This function adopts raw data for more convinient usage.
    """
    data = pd.read_csv(party_data_path)
    Data = pd.read_excel(surveillance_data, sheet_name=None)
    population = pd.read_csv(population_data_path)

    data_pol = None
    for i in range(16):
        data_part = data.iloc[:,i*9+1:i*9+10]
        reg = data_part.columns[0]
        data_part.columns = list(map(lambda x: x[3:] if '_' in x else 'orders', data_part.columns))
        data_part['year'] = data.iloc[:,0]
        data_part['state'] = reg
        data_pol = pd.concat([data_pol, data_part], axis=0) if data_pol is not None else data_part


    data_orders = None
    for k in Data.keys():
        data_y = Data[k]
        data_y = data_y.groupby('paragraph').sum().T.reset_index()
        data_y['state'] = data_y['index']
        data_y['year'] = int(k[:4])
        data_orders = pd.concat([data_orders, data_y], axis=0) if data_orders is not None else data_y

    data_orders.columns = [x if isinstance(x, str) else 'cases_' + str(x) for x in data_orders.columns]

    population = pd.melt(population, id_vars=['state'], value_vars=population.columns[1:])
    population.columns = ['state', 'year', 'population']
    population['year'] = population.year.astype('int64')

    data = data_pol.merge(data_orders, on=['state', 'year']).merge(population, on=['state', 'year'])

    data[['Reg1', 'Reg2', 'Reg3']] = data[['Reg1', 'Reg2', 'Reg3']].replace(['0', 0], '')
    data['parties'] = (data.Reg1 
                    + ' ' + data.Reg2
                    + ' ' + data.Reg3).apply(lambda x: tuple(sorted(x.split())))

    data['case_4_proba'] = data.cases_4 / data.population

    return data, Data, population


def load_gdp_data(geo_df_path: str) -> pd.DataFrame:
    geo_df = pd.read_csv(geo_df_path)
    geo_df['geometry'] = geo_df.geometry.apply(loads)
    geo_df = gpd.GeoDataFrame(geo_df, crs='EPSG:4326')
    geo_df['coords'] = geo_df.geometry.apply(lambda x: x.representative_point().coords[:][0])
    return geo_df


def plot_map(
        geo_df: pd.DataFrame, 
        column: str, 
        title: str = None, 
        dst_path: str = None) -> None:
    """
    Plot german map with colorbar.
    
    arguments:
    geo_df -- data prepared with `data_to_geo`
    column -- value which is used to indicate levels across states, e.g. 'cases_3_per_1k'
    title -- plot titile
    dst_path -- if provided save figure, e.g. './map_rel_2021.png'
    """
    cmap = 'Blues' # can use other like 'Reds'
    fig, ax = plt.subplots(1, figsize=(20, 6 ))

    ax = geo_df.plot(column=column, ax=ax, edgecolor='0.8', linewidth=1, cmap=cmap)
    ax.set_title(title, fontdict={'fontsize': '16', 'fontweight': '3'})

    for idx, row in geo_df.iterrows():
        x = row['coords'][0] - 0.1
        y = row['coords'][1]
        text = plt.annotate(
            text=f"{row['state']}",
            xy=(x,y),
            xytext= (x,y), 
            fontsize=11,
            color='black',
        )
        text.set_path_effects([path_effects.Stroke(linewidth=1, foreground='white'),
                           path_effects.Normal()])

    ax.axis('off')
    
    vmin, vmax = geo_df[column].min(), geo_df[column].max()
    sm = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=vmin, vmax=vmax), cmap=cmap)
    cbaxes = fig.add_axes([0.35, 0.125, 0.01, 0.75])
    cbar = fig.colorbar(sm, cax=cbaxes)
    if dst_path:
        plt.savefig(dst_path, dpi=400)

    return fig, ax
