import datetime
import numpy as np
import pandas as pd
from datetime import datetime
import os

csvPath = r"back-end/csvStorage/"

def getDropDates():

    data = pd.read_csv(csvPath + 'issFlightPlan') # change this to where the data is going to be imported
    data = data.copy(deep=True) # copies the data
    data.drop(data[data['event'] != "Dock"].index, inplace = True) # drops rows that does not have Dock in their event column
    data = data[["datedim"]] # gets just the datedim colun and puts it into data
    data["datedim"] = pd.to_datetime(data['datedim']) # turns datedim column to an actual datedim variable to be easily comparable in the next couple of commands
    data.reset_index(drop=True) # resets the index just in case

    # these can be used to calculate the actual date and turn it into a datedim varaible that can be compared to the data['datedim'] function
    # actualDate = datetime.now()
    # actualDate = actualDate.strftime("%d/%m/%Y")
    # actualDate = str(actualDate)
    # actualDate = datetime.strptime(actualDate, "%d/%m/%Y")

    # in the future if there is updated datasets you can undo the comments and replace '2023-9-6' to actualDate 
    data.drop(data[data['datedim'] >= '2023-9-6'].index, inplace = True) 

    return data


def modifyConsumables():
    # gets the consumables csv ofc need to change the read csv part :)
    consumables = pd.read_csv(csvPath + 'IMSConsumables')
    consumables = consumables.copy(deep=True)

    # since this data set does not have headers currently will place the headers with this :)
    consumables.columns =['datedim','id','id_parent','id_path','tree_depth','tree','part_number','serial_number','location_name','original_ip_owner','current_ip_owner','operational_nomenclature','russian_name','english_name','barcode','quantity','width','height','length','diameter','calculated_volume','stwg_ovrrd_vol','children_volume','stwg_ovrrd_chldren_vol','ovrrd_notes','volume_notes','expire_date','launch','type','hazard','state','status','is_container','is_moveable','system','subsystem','action_date','move_date','fill_status','categoryID','category_name']

    # Making sure that the ownder is NASA maybe will need to be deleted 
    consumables = consumables.loc[consumables["current_ip_owner"] == 'NASA']

    # turns the datedim into a YEAR-MONTH-DAY
    consumables['datedim'] = consumables['datedim'].astype(str)
    consumables['datedim'] = consumables['datedim'].apply(lambda x: x if len(x) < 11 else x[:10])
    consumables['datedim'] =  pd.to_datetime(consumables['datedim'])

    # cuts the dataset down to a much more managable 
    consumables = consumables[['datedim','calculated_volume','category_name']]

    return consumables

def getFilledWaterData():
    water = pd.read_csv(csvPath + 'usWeeklyWaterSummary')
    water = water.copy(deep=True)

    water = water[['Date','Corrected Total (L)']]
    # this makes it so that it will fill the dates with the last data and so on
    water['Date'] = pd.to_datetime(water['Date'])
    water = water.set_index('Date').resample('D').ffill().reset_index()

    return water


def getOxygenNitrogen():
    data = pd.read_csv(csvPath + 'weeklyGasSummary')
    data = data.copy(deep=True)

    data = data[['Date','Adjusted O2 (kg)','Adjusted N2 (kg)']]
    # this makes it so that it will fill the dates with the last data and so on
    data['Date'] = pd.to_datetime(data['Date'])
    data = data.set_index('Date').resample('D').ffill().reset_index()

    oxygen = data[['Date','Adjusted O2 (kg)']]
    nitrogen = data[['Date','Adjusted N2 (kg)']]

    return oxygen, nitrogen

def compareRates():

    # copys the dropDates and puts it into dates
    dates = getDropDates()
    consumables = modifyConsumables()
    oxygen, nitrogen= getOxygenNitrogen()
    water = getFilledWaterData()
    #note  does not focus on if us currently owns it
    #ITS ONLY WHICH CATEGORY THIS IS WE CAN MODIFY THIS BY GETTING ANOTHER COLUMN THEN SORTING IT BY THAT THEN DOING THIS 

    usageRateWater = getActualUsageRates2(water,dates)

    usageRateNitrogen = getActualUsageRates2(nitrogen,dates)

    usageRateOxygen = getActualUsageRates2(oxygen,dates)

    filterInsert = consumables.loc[consumables["category_name"] == 'Filter Inserts']
    filterInsert = filterInsert[['datedim', 'calculated_volume']]
    usageRatefilterInsert = getActualUsageRates(filterInsert,dates)

    acyInserts = consumables.loc[consumables["category_name"] == 'ACY Inserts']
    acyInserts = acyInserts[['datedim', 'calculated_volume']]
    usageRateacyInserts = getActualUsageRates(acyInserts,dates)

    KTO = consumables.loc[consumables["category_name"] == 'KTO']
    KTO = KTO[['datedim', 'calculated_volume']]
    usageRateKTO = getActualUsageRates(KTO,dates)

    pretreat = consumables.loc[consumables["category_name"] == 'Pretreat Tanks']
    pretreat = pretreat[['datedim', 'calculated_volume']]
    usageRatepretreat = getActualUsageRates(pretreat,dates)

    # foodRS = consumables.loc[consumables["category_name"] == 'Food-RS']
    # foodRS = foodRS[['datedim', 'calculated_volume']]
    # foodRS = getActualUsageRates(foodRS,dates)

    foodUS = consumables.loc[consumables["category_name"] == 'Food-US']  
    foodUS = foodUS[['datedim', 'calculated_volume']]
    usageRatefoodUS = getActualUsageRates(foodUS,dates)

    #EDV = consumables.loc[consumables["category_name"] == 'EDV']
    #EDV = EDV[['datedim', 'calculated_volume']]
    #usageRateEDV = getActualUsageRates(EDV,dates)

    return usageRateWater,usageRateNitrogen,usageRateOxygen,usageRatefilterInsert,usageRateKTO,usageRatepretreat,usageRatefoodUS #,usageRateEDV


def getActualUsageRates(dataSet,dates):

    #sums the calculated volume based on dates in the datedim column
    dataSet=dataSet.groupby("datedim", group_keys=False, as_index=False).sum()

    # does an intersetion between dates and dateset via the datedim column
    mergedData = pd.merge(dataSet, dates, how ='inner', on=['datedim'])

    #initializing a list
    result = []
    days = []
    difference = []
    datesOfMission = []

    # initilalizing a final dataframe
    final = pd.DataFrame()

    # getting the lenght of the dataframe
    length = len(mergedData.index)

    for index, row in mergedData.iterrows():
        if index + 1 != length:
            dividen = mergedData.at[index + 1, 'calculated_volume'] - mergedData.at[index, 'calculated_volume']
            divisor = mergedData.at[index + 1, 'datedim'] - mergedData.at[index, 'datedim']
            # appends dividen and divisor to days and difference so that we are able to create a dataframe
            difference.append(dividen)
            days.append(divisor)
            result.append(dividen/divisor.days)

            # formats the datedim into much more readable format
            temp1 = mergedData.at[index, 'datedim']
            temp1 = temp1.strftime("%B %d, %Y")

            temp2 = mergedData.at[index + 1, 'datedim']
            temp2 = temp2.strftime("%B %d, %Y")

            datesOfMission.append(temp1 + ' - ' + temp2)

    final['datesOfMission'] = datesOfMission
    final['number_of_days'] = days
    final['Difference'] = difference
    final['rates'] = result        

    return final

def getActualUsageRates2(dataSet,dates):

    dataSet = dataSet.rename(columns={'Date': 'datedim'})
    dataSet = dataSet.rename(columns={dataSet.columns[1]: 'calculated_volume'})
    #sums the calculated volume based on dates in the datedim column
    dataSet=dataSet.groupby("datedim", group_keys=False, as_index=False).sum()

    # does an intersetion between dates and dateset via the datedim column
    mergedData = pd.merge(dataSet, dates, how ='inner', on=['datedim'])

    #initializing a list
    result = []
    days = []
    difference = []
    datesOfMission = []

    # initilalizing a final dataframe
    final = pd.DataFrame()

    # getting the lenght of the dataframe
    length = len(mergedData.index)

    for index, row in mergedData.iterrows():
        if index + 1 != length:
            dividen = mergedData.at[index + 1, 'calculated_volume'] - mergedData.at[index, 'calculated_volume']
            divisor = mergedData.at[index + 1, 'datedim'] - mergedData.at[index, 'datedim']
            # appends dividen and divisor to days and difference so that we are able to create a dataframe
            difference.append(dividen)
            days.append(divisor)
            result.append(dividen/divisor.days)

            # formats the datedim into much more readable format
            temp1 = mergedData.at[index, 'datedim']
            temp1 = temp1.strftime("%B %d, %Y")

            temp2 = mergedData.at[index + 1, 'datedim']
            temp2 = temp2.strftime("%B %d, %Y")

            datesOfMission.append(temp1 + ' - ' + temp2)

    final['datesOfMission'] = datesOfMission
    final['number_of_days'] = days
    final['Difference'] = difference
    final['rates'] = result        

def calculateCurrentRate():
    data = pd.read_csv(csvPath + 'ratesDefinition') # needs to be changed
    data = data.copy(deep=True)

    
    consumablesEveryone = data.drop(data[(data['affected_consumable'] == 'US Food BOBs') |
                                     (data['affected_consumable'] == 'RS Food Rations') |
                                     (data['affected_consumable'] == 'ACY Inserts') |
                                     (data['affected_consumable'] == 'KTO') |
                                     (data['affected_consumable'] == 'Pretreat Tanks') |
                                     (data['affected_consumable'] == 'Filter Inserts') |
                                     (data['affected_consumable'] == 'Urine Receptacle')].index)

    consumablesNASA = data.drop(data[(data['affected_consumable'] == 'Oxygen') |
                                     (data['affected_consumable'] == 'Air') |
                                     (data['affected_consumable'] == 'Nitrogen') |
                                     (data['affected_consumable'] == 'Oxygen') |
                                     (data['affected_consumable'] == 'Water')].index)

    #consumablesNASA['adjusted_rate'] = data.apply(adjust_rate, axis=1)
    
    #consumablesEveryone['adjusted_rate'] = data.apply(adjust_rate, axis=1)
    consumablesEveryone['rate'] = consumablesEveryone.apply(baased, axis=1)
    consumablesEveryone
    consumablesEveryone = consumablesEveryone[['affected_consumable','rate']]
    consumablesEveryone= consumablesEveryone.groupby('affected_consumable', group_keys=False, as_index=False).sum(numeric_only=True)

    consumablesNASA = consumablesNASA[['affected_consumable','rate']]
    consumablesNASA= consumablesNASA.groupby('affected_consumable', group_keys=False, as_index=False).sum()
    rates = consumablesNASA.append(consumablesEveryone)
    return rates

def baased(row):
    if 'generation' in row['type']:
        return -1 * row['rate']
    else:
        return row['rate']
     

def compare():
    usageRateWater,usageRateNitrogen,usageRateOxygen,usageRatefilterInsert,usageRateKTO,usageRatepretreat,usageRatefoodUS = compareRates()
    rates = calculateCurrentRate()

    usageRateWater['rate_definition'] = rates[rates['affected_consumable'] == 'Water']["rate"].values[0]
    usageRateNitrogen['rate_definition'] = rates[rates['affected_consumable'] == 'Nitrogen']["rate"].values[0]
    usageRateOxygen['rate_definition'] = rates[rates['affected_consumable'] == 'Oxygen']["rate"].values[0]
    usageRatefilterInsert['rate_definition'] = rates[rates['affected_consumable'] == 'Filter Inserts']["rate"].values[0]
    usageRateKTO['rate_definition'] = rates[rates['affected_consumable'] == 'KTO']["rate"].values[0]
    usageRatepretreat['rate_definition'] = rates[rates['affected_consumable'] == 'Pretreat Tanks']["rate"].values[0]
    usageRatefoodUS['rate_definition'] = rates[rates['affected_consumable'] == 'US Food BOBs']["rate"].values[0]

    usageRateWater['percentageDiffirence'] = usageRateWater.apply(lambda row: (abs(row['rate_definition'] - row['rates']) / ((row['rates'] + row['rate_definition']) / 2 )) * 100 if row['rates'] != 0 else 0, axis=1)
    usageRateNitrogen['percentageDiffirence'] =usageRateNitrogen.apply(lambda row: (abs(row['rate_definition'] - row['rates']) / ((row['rates'] + row['rate_definition']) / 2 )) * 100 if row['rates'] != 0 else 0, axis=1)
    usageRateOxygen['percentageDiffirence'] =usageRateOxygen.apply(lambda row: (abs(row['rate_definition'] - row['rates']) / ((row['rates'] + row['rate_definition']) / 2 )) * 100 if row['rates'] != 0 else 0, axis=1)
    usageRatefilterInsert['percentageDiffirence'] =usageRatefilterInsert.apply(lambda row: (abs(row['rate_definition'] - row['rates']) / ((row['rates'] + row['rate_definition']) / 2 )) * 100 if row['rates'] != 0 else 0, axis=1)
    usageRateKTO['percentageDiffirence'] = usageRateKTO.apply(lambda row: (abs(row['rate_definition'] - row['rates']) / ((row['rates'] + row['rate_definition']) / 2 )) * 100 if row['rates'] != 0 else 0, axis=1)
    usageRatepretreat['percentageDiffirence'] = usageRatepretreat.apply(lambda row: (abs(row['rate_definition'] - row['rates']) / ((row['rates'] + row['rate_definition']) / 2 )) * 100 if row['rates'] != 0 else 0, axis=1)
    usageRatefoodUS['percentageDiffirence'] = usageRatefoodUS.apply(lambda row: (abs(row['rate_definition'] - row['rates']) / ((row['rates'] + row['rate_definition']) / 2 )) * 100 if row['rates'] != 0 else 0, axis=1)

    path = r"prediction/PredictionsCSV/"
    usageRateWater.to_csv(path + 'usageRateWater.csv')
    usageRateNitrogen.to_csv(path + 'usageRateNitrogen.csv')
    usageRateOxygen.to_csv(path + 'usageRateOxygen.csv')
    usageRatefilterInsert.to_csv(path + 'usageRatefilterInsert.csv')
    usageRateKTO.to_csv(path + 'usageRateKTO.csv')
    usageRatepretreat.to_csv(path + 'usageRatepretreat.csv')
    usageRatefoodUS.to_csv(path + 'usageRatefoodUS.csv')

    return 
compare()
