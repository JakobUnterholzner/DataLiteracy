"""
    Original code is provided by Prof. Philipp Hennig on "Data Literacy" course. Tübingen, 2023
    This script is a streamlit app. You can run it on your machine by installing streamlit via pip and then running
    `streamlit run estimators_sl.py` in your terminal.
    (requires python 3.10 or higher, streamlit, matplotlib, numpy, tueplots)
"""
import streamlit as st
import matplotlib.pyplot as plt
from tueplots import bundles
from tueplots.constants.color import rgb
from scipy.stats import multinomial

import pandas as pd
import matplotlib.pyplot as pltç
import matplotlib.patheffects as path_effects

import pandas as pd
import geopandas as gpd
import geofunctions as gf

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
data, Data, population = gf.prepare_datasets(
    '../dat/tele_and_gov_data.csv',
    '../dat/surveillance_data.xlsx',
    '../dat/12411-0010-DLAND_population.csv'
)

data['case_4_proba'] = (data.cases_4 / data.population * 100).apply(lambda x: round(x,3)).astype(str)

geo_df = gf.load_gdp_data('../dat/ne_10m_admin_1_states_provinces/DE_shapes.csv')

geo_data = geo_df.merge(data, on = 'state')
geo_data['cases_6'] = geo_data.cases_6.apply(lambda x: 1 if x == 0 else x)
geo_data['laws_per_order'] = geo_data.cases_6 / geo_data.cases_4


# =============================================================================================
# Plotting

data_year = geo_data.query(f'year=={year}')
I_to_col =  {'P(s)': 'case_4_proba', 'LPO': 'laws_per_order'}
col_to_I = {'case_4_proba': 'P(s), %', 'laws_per_order': 'LPO'}
column = I_to_col[value]
pd.options.display.float_format = '{:,.f6}'.format

fig, ax = gf.plot_map(data_year, column)
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
