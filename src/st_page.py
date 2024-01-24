"""
    Original code is provided by Prof. Philipp Hennig on "Data Literacy" course. Tübingen, 2023
    This script is a streamlit app. You can run it on your machine by installing streamlit via pip and then running
    `streamlit run estimators_sl.py` in your terminal.
    (requires python 3.10 or higher, streamlit, matplotlib, numpy, tueplots)
"""
import streamlit as st
from matplotlib import pyplot as plt
from tueplots import bundles
from tueplots.constants.color import rgb
from scipy.stats import multinomial

import pandas as pd
import matplotlib.pyplot as pltç
import matplotlib.patheffects as path_effects

import pandas as pd
import geopandas as gpd
from shapely.wkt import loads


plt.rcParams.update(bundles.beamer_moml())

st.set_page_config(
    page_title="Surveillance",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "(c) Khomutov Andrey, 2023"},
)

# =============================================================================================

st.sidebar.title("Parameters")

st.sidebar.markdown("# Map")

year = st.sidebar.selectbox("Year", [2021, 2020, 2019, 2016, 2013])
value = st.sidebar.selectbox("Indicator", ['P(s)', 'LPO'])
st.sidebar.markdown("* P(s) - probability to be surveilled \n * LPO - mean number of laws applied for each order")

show_table = st.sidebar.checkbox("Show table", value=False)    

st.sidebar.markdown("# State stats")
state_names = {'SN': 'Sachsen', 'BY': 'Bayern', 'RP': 'Rheinland-Pfalz', 'SL': 'Saarland', 'SH': 'Schleswig-Holstein',
 'NI': 'Niedersachsen', 'NW': 'Nordrhein-Westfalen', 'BW': 'Baden-Württemberg', 'BB': 'Brandenburg', 'MV': 'Mecklenburg-Vorpommern',
 'HB': 'Bremen', 'HH': 'Hamburg', 'HE': 'Hessen', 'TH': 'Thüringen', 'ST': 'Sachsen-Anhalt', 'BE': 'Berlin'}

state = st.sidebar.selectbox("State", [k+' - '+state_names[k] for k in state_names.keys()])
state = state.split(' - ')[0]

# =============================================================================================
# Computing stuff
data = pd.read_csv('../dat/tele_and_gov_data.csv')

data_pol = None
for i in range(16):
    data_part = data.iloc[:,i*9+1:i*9+10]
    reg = data_part.columns[0]
    data_part.columns = list(map(lambda x: x[3:] if '_' in x else 'orders', data_part.columns))
    data_part['year'] = data.iloc[:,0]
    data_part['state'] = reg
    data_pol = pd.concat([data_pol, data_part], axis=0) if data_pol is not None else data_part


Data = pd.read_excel('../dat/surveillance_data.xlsx', sheet_name=None)

data_orders = None
for k in Data.keys():
    data_y = Data[k]
    data_y = data_y.groupby('paragraph').sum().T.reset_index()
    data_y['state'] = data_y['index']
    data_y['year'] = int(k[:4])
    data_orders = pd.concat([data_orders, data_y], axis=0) if data_orders is not None else data_y

data_orders.columns = [x if isinstance(x, str) else 'cases_' + str(x) for x in data_orders.columns]


population = pd.read_csv('../dat/12411-0010-DLAND_population.csv')
population = pd.melt(population, id_vars=['state'], value_vars=population.columns[1:])
population.columns = ['state', 'year', 'population']
population['year'] = population.year.astype('int64')

data = data_pol.merge(data_orders, on=['state', 'year']).merge(population, on=['state', 'year'])

data[['Reg1', 'Reg2', 'Reg3']] = data[['Reg1', 'Reg2', 'Reg3']].replace(['0', 0], '')
data['parties'] = (data.Reg1 
                   + ' ' + data.Reg2
                   + ' ' + data.Reg3).apply(lambda x: tuple(sorted(x.split())))

data['case_4_proba'] = (data.cases_4 / data.population * 100).apply(lambda x: round(x,3)).astype(str)

geo_df = pd.read_csv('../dat/ne_10m_admin_1_states_provinces/DE_shapes.csv')
geo_df['geometry'] = geo_df.geometry.apply(loads)
geo_df = gpd.GeoDataFrame(geo_df, crs='EPSG:4326')
geo_df['coords'] = geo_df.geometry.apply(lambda x: x.representative_point().coords[:][0])

geo_data = geo_df.merge(data, on = 'state')
geo_data['cases_6'] = geo_data.cases_6.apply(lambda x: 1 if x == 0 else x)
geo_data['laws_per_order'] = geo_data.cases_6 / geo_data.cases_4


# =============================================================================================
# Plotting

def plot_map(geo_df: pd.DataFrame, column: str, title: str = None, figname: str = None) -> None:
    """
    Plot german map with colorbar.
    
    arguments:
    geo_df -- data prepared with `data_to_geo`
    column -- value which is used to indicate levels across states, e.g. 'cases_3_per_1k'
    title -- plot titile
    figname -- if provided save figure, e.g. 'map_rel_2021.png'
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
    if figname:
        plt.savefig(figname, dpi=400)

    return fig, ax


data_year = geo_data.query(f'year=={year}')
I_to_col =  {'P(s)': 'case_4_proba', 'LPO': 'laws_per_order'}
col_to_I = {'case_4_proba': 'P(s), %', 'laws_per_order': 'LPO'}
column = I_to_col[value]
pd.options.display.float_format = '{:,.f6}'.format
fig, ax = plot_map(data_year, column)
col1, col2 = st.columns(2)
with col1:
    st.markdown(f'### Indicator level in states: {col_to_I[column]}')
    st.pyplot(fig, use_container_width=True)
    if show_table:
        st.markdown(f'### Exact values')
        pre_df = data_year.sort_values(column, ascending=False).reset_index()[['state', 'name', 'population'] + [column]]
        pre_df.columns = [col_to_I[c] if c in col_to_I.keys() else c for c in pre_df.columns]
        st.table(pre_df)



crimes = Data['2021_surveillance'].query('paragraph==6')[['subparagraph', 'description_en']]
crimes['crime'] = crimes.description_en.apply(lambda x: x[:x.find('(')])

data_state = Data[f'{year}_surveillance'].merge(crimes, on='subparagraph')
data_state['total'] = data_state[state]
data_state['p, %'] = (data_state.total / data_state.total.sum() * 100).apply(lambda x: round(x,1)).astype(str)

with col2:
    st.markdown(f'### {state_names[state]} most survilled crimes')
    data_state = data_state.sort_values('total', ascending=False).reset_index()[['crime', 'total', 'p, %']]
    st.table(data_state.head(5))

    st.markdown(f'### {state_names[state]} stats')
    population = '{:,}'.format(geo_data.query(f'year=={year} and state=="{state}"').population.item())
    p_s = geo_data.query(f'year=={year} and state=="{state}"').case_4_proba.item()
    lpo = geo_data.query(f'year=={year} and state=="{state}"').laws_per_order.item()
    st.markdown(f' * Population: {population}')
    st.markdown(f' * P(s): {p_s}%')
    st.markdown(f' * LPO: {round(lpo,2)}')
