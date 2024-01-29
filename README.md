# Structure
![Trend_States](.doc/fig/fig_trend.pdf)

# Data
> Main data is taken from Bundesjustizamt [Statistiken der Rechtspflege](https://www.bundesjustizamt.de/DE/Service/Justizstatistiken/Justizstatistiken_node.html#AnkerDokument44152) web page.\
`surveillance_data.xlsx` conatains full data for years 2013, 2016, 2019-2022, and the number of inital on prolonged orders (§4) for 2008-2021 on separate sheets.
> Population data was aquired in *GENESIS-Online* [database](https://www-genesis.destatis.de/genesis//online?operation=table&code=12411-0010&bypass=true&levelindex=0&levelid=1705062410665#abreadcrumb) of the Federal Statistical Office 
> data for development of number of mobile device users in Germany: https://www.bundesnetzagentur.de/DE/Fachthemen/Telekommunikation/Marktdaten/Mobilfunkteilnehmer/artikel.html
> data regarding federal governments is stored in dat/election_results_per_states folder
![Trend_States](.doc/fig/fig_trend_and_users.pdf)
# Assumptions
> Judges are appointed by the state governments (simplification, does not live up to legal processes in detail)
> 



# Hypotheses
> The trend of correlation between number of mobile device users and surveillance orders continued (compared to the data between 1990 and 2000)
> Null: there is no correlation between political parties in the different states and the number of surveillance orders

# Results
Ineractive data is available via `streamlit` interface 
```console
streamlit run ./src/st_page.py
```
![sample_st](./doc/fig/sample_st.gif)
