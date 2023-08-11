import pandas as pd
import geopandas as gpd
import numpy as np

def inputdata(wellid,datapr,GWfilldatamod):
    """ Create a dataframe with the GWL time series, the precipitation time series
        associated to it and the corresponding monthly dates
    Inputs:  
            wellid: id of the selected well
            datapr: pickle data of daily precipitation values extracted from HYRAS netCDF
            GWfilldatamod: pickle with the GWL time series storaged"""
    df=datapr.loc[datapr.ID==int(wellid)]
    indexm=df.index.values[0]
    #set dates as a column
    df_day=pd.DataFrame({"dates":pd.to_datetime(df.time[indexm]),
                               "cdata":df.cdata[indexm]} )
    df_dayc=df_day.copy()
    #resample to monthly resolution
    dfcdmonth=df_dayc.resample("M", on="dates").sum()
    dfcdmonth['dates'] = dfcdmonth.index.strftime("%Y-%m") 


    dfgwl=GWfilldatamod.loc[GWfilldatamod.wellid==int(wellid)]
    indv=dfgwl.index.values[0]
    datfill=dfgwl.GW_NN[indv]
    try:
        dfwell=datfill[["DATUM","twell_"+str(wellid)]]
    except:
        dfwell=datfill[["DATUM","Ftwell_"+str(wellid)]]

    dateini=dfwell.DATUM[0]  if  dfwell.DATUM[0]>dfcdmonth.index[0] else dfcdmonth.index[0]
    datefin=dfcdmonth.index[-1] if dfwell.DATUM[len(dfwell)-1] >= dfcdmonth.index[-1] else dfwell.DATUM[len(dfwell)-1]
    dates= pd.date_range(dateini,datefin, freq='M')
    #Make sure the data has the same time range 
    dfwellsel=dfwell.loc[(dfwell.DATUM>=dateini) & (dfwell.DATUM<=datefin)]

    dfdat=dfcdmonth.loc[(dfcdmonth.dates>=dateini.strftime("%Y-%m")) & (dfcdmonth.dates<=datefin.strftime("%Y-%m"))]
    try:
        cdwell=pd.DataFrame({"dates":dates,
                             "GWL": dfwellsel["twell_"+str(wellid)], 
                             "pr":dfdat.cdata.values})
    except:
        cdwell=pd.DataFrame({"dates":dates,
                             "GWL": dfwellsel["Ftwell_"+str(wellid)], 
                             "pr":dfdat.cdata.values})
    return cdwell

def lagged_correlations(lwellid, datapr, GWfilldatamod):
    l2=[]
    for lw in lwellid:
        try:
            cdwell=inputdata(lw,datapr, GWfilldatamod)
            l=[]
            for i in range(12): #correlations of 12 months
                lagged_correlations = cdwell['GWL'].corr(cdwell['pr'].shift(i))
                l.append(lagged_correlations)
            l2.append(max(l))

        except:
            continue  
    return l2