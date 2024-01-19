# Structure
See lecture 10 for how the repo is designed. In short:

>dat -> stores the data\
src -> stores larger models or function\
exp -> stores the experiments we performed\
doc -> DataLitReport -> stores the tex file\
doc -> fig -> stores figures (PDF) and scripts that create the figures (.py)

# Data
> Main data is taken from Bundesjustizamt [Statistiken der Rechtspflege](https://www.bundesjustizamt.de/DE/Service/Justizstatistiken/Justizstatistiken_node.html#AnkerDokument44152) web page.\
`surveillance_data.xlsx` conatains data for years 2013, 2016, 2019-2022 on separate sheets

> Population data was aquired in *GENESIS-Online* [database](https://www-genesis.destatis.de/genesis//online?operation=table&code=12411-0010&bypass=true&levelindex=0&levelid=1705062410665#abreadcrumb) of the Federal Statistical Office 

> data for development of number of mobile device users in Germany: https://www.bundesnetzagentur.de/DE/Fachthemen/Telekommunikation/Marktdaten/Mobilfunkteilnehmer/artikel.html
> 

# Assumptions
> Judges are appointed by the state governments (simplification, does not live up to legal processes in detail)
> GBA (Generalbundesanwalt = Federal Prosecutor General) not regarded in analysis, although not insignificant part of surveillance orders can be attributed to him)
> 



# Hypotheses
> The trend of correlation between number of mobile device users and surveillance orders continued (compared to the data between 1990 and 2000)
> Null: there is no correlation between political parties in the different states and the number of surveillance orders

# Results
>
>
