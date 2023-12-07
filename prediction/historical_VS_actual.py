import datetime
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta 
import os

asd = os.getcwd()
csvPath = (os.getcwd() +"/back-end/csvStorage/")

def getDropDates(): # this is done
    data = pd.read_csv(csvPath + 'issFlightPlan.csv') # change this to where the data is going to be imported
    data = data.copy(deep=True) # copies the data
    data.drop(data[data['event'] != "Dock"].index, inplace = True) # drops rows that does not have Dock in their event column
    words = ['NG', 'SpX', 'Progress', 'Ax', 'HTV-X']

    # Create a boolean mask where True indicates the rows to be dropped
    mask = data['vehicle_name'].str.contains('|'.join(words))

    # keep rows that contain the words
    data = data[mask]

    data = data[["datedim"]] # gets just the datedim colun and puts it into data
    data["datedim"] = pd.to_datetime(data['datedim']) # turns datedim column to an actual datedim variable to be easily comparable in the next couple of commands
    data.reset_index(drop=True) # resets the index just in case

    # these can be used to calculate the actual date and turn it into a datedim varaible that can be compared to the data['datedim'] function
    # actualDate = datetime.now()
    # actualDate = actualDate.strftime("%d/%m/%Y")
    # actualDate = str(actualDate)
    # actualDate = datetime.strptime(actualDate, "%d/%m/%Y")

    # in the future if there is updated datasets you can undo the comments and replace '2023-9-6' to actualDate 
    
    return data


def modifyConsumables():
    # gets the consumables csv ofc need to change the read csv part :)
    consumables = pd.read_csv(csvPath + 'consumables.csv')
    storedConsumables = pd.read_csv(csvPath + 'storedItemsOnlyIMS.csv')
    consumables = consumables.copy(deep=True)
    storedConsumables = storedConsumables.copy(deep=True)
    storedConsumables['datedim'] = pd.to_datetime(storedConsumables['datedim'])

    # since this data set does not have headers currently will place the headers with this :)
    consumables.columns =['datedim','id','id_parent','id_path','tree_depth','tree','part_number','serial_number','location_name','original_ip_owner','current_ip_owner','operational_nomenclature','russian_name','english_name','barcode','quantity','width','height','length','diameter','calculated_volume','stwg_ovrrd_vol','children_volume','stwg_ovrrd_chldren_vol','ovrrd_notes','volume_notes','expire_date','launch','type','hazard','state','status','is_container','is_moveable','system','subsystem','action_date','move_date','fill_status','categoryID','category_name']
    
    consumables = pd.concat([consumables,storedConsumables])
    
    
    # Making sure that the ownder is NASA maybe will need to be deleted 
    consumables = consumables.loc[consumables["current_ip_owner"] == 'NASA']

    # turns the datedim into a YEAR-MONTH-DAY
    consumables['datedim'] = consumables['datedim'].astype(str)
    consumables['datedim'] = consumables['datedim'].apply(lambda x: x if len(x) < 11 else x[:10])
    consumables['datedim'] =  pd.to_datetime(consumables['datedim'])

    # cuts the dataset down to a much more managable 
    consumables = consumables[['datedim','quantity','category_name']]

    return consumables

def getFilledWaterData():
    water = pd.read_csv(csvPath + 'usWeeklyWaterSummary.csv')
    water = water.copy(deep=True)

    water = water[['Date', 'Corrected Total (L)']]
    # this makes it so that it will fill the dates with the last data and so on
    water['Date'] = pd.to_datetime(water['Date'])

    water.rename({'Date': 'datedim','Corrected Total (L)' : 'total'}, axis=1, inplace=True)
    return water


def getOxygenNitrogen():
    data = pd.read_csv(csvPath + 'weeklyGasSummary.csv')
    data = data.copy(deep=True)

    data = data[['Date','Adjusted O2 (kg)','Adjusted N2 (kg)']]
    # this makes it so that it will fill the dates with the last data and so on
    data['Date'] = pd.to_datetime(data['Date'])


    oxygen = data[['Date','Adjusted O2 (kg)']]
    nitrogen = data[['Date','Adjusted N2 (kg)']]
    oxygen.rename({'Date': 'datedim','Adjusted O2 (kg)' : 'total'}, axis=1, inplace=True)
    nitrogen.rename({'Date': 'datedim','Adjusted N2 (kg)' : 'total'}, axis=1, inplace=True)
    return oxygen, nitrogen

def compareRates():
    # copys the dropDates and puts it into dates
    dates = getDropDates()
    consumables = modifyConsumables()

    #note  does not focus on if us currently owns it
    #ITS ONLY WHICH CATEGORY THIS IS WE CAN MODIFY THIS BY GETTING ANOTHER COLUMN THEN SORTING IT BY THAT THEN DOING THIS 
    
    filterInsert = consumables.loc[consumables["category_name"] == 'Filter Inserts']
    filterInsert = filterInsert[['datedim', 'quantity']]
    filterInsert=filterInsert.groupby("datedim", group_keys=False, as_index=False).sum()

    acyInserts = consumables.loc[consumables["category_name"] == 'ACY Inserts']
    acyInserts = acyInserts[['datedim', 'quantity']]
    acyInserts=acyInserts.groupby("datedim", group_keys=False, as_index=False).sum()

    KTO = consumables.loc[consumables["category_name"] == 'KTO']
    KTO = KTO[['datedim', 'quantity']]
    KTO=KTO.groupby("datedim", group_keys=False, as_index=False).sum()

    pretreat = consumables.loc[consumables["category_name"] == 'Pretreat Tanks']
    pretreat = pretreat[['datedim', 'quantity']]
    pretreat=pretreat.groupby("datedim", group_keys=False, as_index=False).sum()
  
    foodUS = consumables.loc[consumables["category_name"] == 'Food-US']  
    foodUS = foodUS[['datedim', 'quantity']]
    foodUS=foodUS.groupby("datedim", group_keys=False, as_index=False).sum()

    return filterInsert,KTO,pretreat,foodUS,acyInserts #,usageRateEDV

    
def calculateCurrentRate():
    data = pd.read_csv(csvPath + 'ratesDefinition.csv') # needs to be changed
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


    consumablesEveryone = consumablesEveryone.drop(consumablesEveryone[(consumablesEveryone['rate_category'] == 'RSOS Crew Water Consumption (Food/Drinking)') | 
                                                                        (consumablesEveryone['rate_category'] == 'RSOS Condensate Processed to Potable')].index)
    consumablesEveryone = consumablesEveryone[['affected_consumable','rate','units','type']]


    consumablesNASA = consumablesNASA[['affected_consumable','rate']]


    return consumablesNASA, consumablesEveryone

    
def baased(row):
    if 'generation' in row['type']:
        return -1 * row['rate']
    else:
        return row['rate']
    
def numCrew():
    crew = pd.read_csv(csvPath + 'issFlightPlanCrew.csv')
    crew = crew.copy(deep=True)

    # crew without russians :)
    nasa = crew[crew.nationality_category != 'RSA']
    nasa = nasa[nasa.nationality_category != 'Commercial']
    nasa = nasa[nasa.nationality_category != 'SFP']
    nasa = nasa[nasa.nationality_category != 'RSA, TBD']

    nasa = nasa.groupby('datedim', group_keys=False, as_index=False).sum()
    everyone = crew.groupby('datedim', group_keys=False, as_index=False).sum()

    # turns columns into datetime
    nasa["datedim"] = pd.to_datetime(nasa['datedim'])
    everyone["datedim"] = pd.to_datetime(everyone['datedim'])
    
    return everyone, nasa

def calculateActualRate():
    consumablesNASA, consumablesEveryone = calculateCurrentRate()
    actual = pd.DataFrame()

    # gets all the type that generates and then sums them all together 
    temp = consumablesEveryone[consumablesEveryone['type'] == 'generation']
    temp = temp.groupby("affected_consumable", as_index=False).sum(numeric_only=True)[['rate', 'affected_consumable']]
    temp = temp.rename(columns={"rate": "generation"})

    # gets all the units that have crew and then sums them all together
    temp1 = consumablesEveryone[consumablesEveryone['units'].str.contains('Crew', case=False)]
    temp1 = temp1.groupby("affected_consumable", as_index=False).sum(numeric_only=True)[['rate', 'affected_consumable']]
    temp1 = temp1.rename(columns={"rate": "rate_per_crew/day"})

    # Remove rows with 'Crew' in the 'units' column
    consumablesEveryone.drop(consumablesEveryone[consumablesEveryone['type'] == 'generation'].index, inplace=True)
    consumablesEveryone = consumablesEveryone[~consumablesEveryone['units'].str.contains('Crew', case=False)]
    consumablesEveryone = consumablesEveryone[~consumablesEveryone['units'].str.contains('Crew', case=False)]
    consumablesEveryone = consumablesEveryone.groupby("affected_consumable", as_index=False).sum(numeric_only=True)[['rate', 'affected_consumable']]
    consumablesEveryone = consumablesEveryone.rename(columns={"rate": "rate_per_day"})

    # Combine the results
    actual = pd.merge(temp, temp1, on="affected_consumable", how="outer")
    actual = pd.merge(actual, consumablesEveryone, on="affected_consumable", how="outer")
    actual = actual.fillna(0)
    actual.reset_index(drop=True, inplace=True)
    return actual

def ifCrew(row):
    if 'Crew' in row['units']:
        return None
    else:
        return row
    
def test2(startDate,endDate):
    numAll, numNASA = numCrew()
    consumablesNASA, filler = calculateCurrentRate()
    consumablesEveryone = calculateActualRate()
    oxygen, nitrogen= getOxygenNitrogen()
    water = getFilledWaterData()

    #turns the variables into datetime
    startDate = datetime.strptime(startDate, '%Y-%m-%d')
    endDate = datetime.strptime(endDate, '%Y-%m-%d')

    # number of days between start and end 
    numNASA.drop(numNASA[numNASA['datedim'] < startDate].index, inplace=True)
    numNASA.drop(numNASA[numNASA['datedim'] > endDate].index, inplace=True)
    numNASA = numNASA.reset_index()
    numAll.drop(numAll[numAll['datedim'] < startDate].index, inplace=True)
    numAll.drop(numAll[numAll['datedim'] > endDate].index, inplace=True)
    numAll = numAll.reset_index()

    # initializes a dataframe
    result = pd.DataFrame()

    # fills the dataframe from startdate to end date
    result['datedim'] = pd.date_range(start = startDate, end = endDate)
    result["datedim"] = pd.to_datetime(result['datedim'])
    result1 = result.copy()
    # Merge with left join to keep only the rows with corresponding dates in oxygen
    merged_data = pd.merge(result, oxygen, on='datedim', how='left')
    merged_data.reset_index(drop=True, inplace=True)
    # Filter out rows where 'total' is not null (indicating a match with the oxygen DataFrame)
    filtered_result_data = merged_data[merged_data['total'].notnull()]

    # Drop the 'total' column as it's no longer needed
    filtered_result_data = filtered_result_data.drop(columns='total')

    # gets the number of crew and puts it into the table also get the length
    result = pd.merge(filtered_result_data, numNASA, on='datedim', how='inner')
    result.rename(columns={'crew_count': 'nasa_crew'}, inplace=True)
    result.reset_index(drop=True, inplace=True)
    result = pd.merge(result, numAll, on='datedim', how='inner')
    result.rename(columns={'crew_count': 'all_crew'}, inplace=True)
    result['days_since_resupply'] = pd.RangeIndex(len(result.index))
    result.reset_index(drop=True, inplace=True)


    # Merge with left join to keep only the rows with corresponding dates in oxygen
    merged_data = pd.merge(result1, water, on='datedim', how='left')

    # Filter out rows where 'total' is not null (indicating a match with the oxygen DataFrame)
    filtered_result_data = merged_data[merged_data['total'].notnull()]

    # Drop the 'total' column as it's no longer needed
    filtered_result_data = filtered_result_data.drop(columns='total')

    # gets the number of crew and puts it into the table also get the length
    result1 = pd.merge(filtered_result_data, numNASA, on='datedim', how='inner')
    result1.rename(columns={'crew_count': 'nasa_crew'}, inplace=True)
    result1.reset_index(drop=True, inplace=True)
    result1 = pd.merge(result1, numAll, on='datedim', how='inner')
    result1.rename(columns={'crew_count': 'all_crew'}, inplace=True)
    result1.reset_index(drop=True, inplace=True)
    result1['days_since_resupply'] = pd.RangeIndex(len(result1.index))

    # initlialzes other tables
    resultOxygen = result.copy()
    resultNitrogen = result.copy()
    resultWater = result1.copy()

    resultOxygen['generation'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Oxygen']["generation"].values[0]
    resultNitrogen['generation'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Water']["generation"].values[0]
    resultWater['generation'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Nitrogen']["generation"].values[0]

    resultOxygen['rate_per_crew/day'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Oxygen']["rate_per_crew/day"].values[0]
    resultNitrogen['rate_per_crew/day'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Water']["rate_per_crew/day"].values[0]
    resultWater['rate_per_crew/day'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Nitrogen']["rate_per_crew/day"].values[0]

    resultOxygen['rate_per_day'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Oxygen']["rate_per_day"].values[0]
    resultNitrogen['rate_per_day'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Water']["rate_per_day"].values[0]
    resultWater['rate_per_day'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Nitrogen']["rate_per_day"].values[0]

    resultOxygen['assumed_loss'] = resultOxygen.apply(calcRate, axis=1)
    resultNitrogen['assumed_loss'] = resultNitrogen.apply(calcRate, axis=1)
    resultWater['assumed_loss'] = resultWater.apply(calcWaterRate, axis=1)

    resultOxygen['actual_value'] = oxygen['total']
    resultNitrogen['actual_value'] = nitrogen['total'] 
    resultWater['actual_value'] = water['total'] 

    oxygen['total1'] = oxygen['total']
    nitrogen['total1'] = nitrogen['total'] 
    water['total1'] = water['total'] 

    oxygen['total1'] = oxygen['total1'].shift(-1)
    nitrogen['total1'] = nitrogen['total1'].shift(-1)
    water['total1'] = water['total1'].shift(-1) 

    oxygen.drop(oxygen[oxygen['datedim'] < startDate].index, inplace=True)
    oxygen.drop(oxygen[oxygen['datedim'] > endDate].index, inplace=True)
    nitrogen.drop(nitrogen[nitrogen['datedim'] < startDate].index, inplace=True)
    nitrogen.drop(nitrogen[nitrogen['datedim'] > endDate].index, inplace=True)
    water.drop(water[water['datedim'] < startDate].index, inplace=True)
    water.drop(water[water['datedim'] > endDate].index, inplace=True)

    oxygen['difference'] = oxygen.apply(subractRows1, axis=1)
    nitrogen['difference'] = nitrogen.apply(subractRows1, axis=1)
    water['difference'] = water.apply(subractRows1, axis=1)

    oxygen = oxygen.reset_index(drop=True)
    nitrogen = nitrogen.reset_index(drop=True)
    water = water.reset_index(drop=True)
    # oxygen['difference'] = oxygen['calculated_volume'] - oxygen['calculated_volume'].iloc[0]
    # nitrogen['difference'] = nitrogen['calculated_volume'] - nitrogen['calculated_volume'].iloc[0]
    # water['difference'] = water['calculated_volume'] - water['calculated_volume'].iloc[0]
    
    resultOxygen['actual_rate_per/day'] = oxygen['difference']
    resultNitrogen['actual_rate_per/day'] = nitrogen['difference']
    resultWater['actual_rate_per/day'] = water['difference']

    #resultOxygen = resultOxygen.fillna(0)
    #resultNitrogen = resultNitrogen.fillna(0)
    #resultWater = resultWater.fillna(0)
    
    #resultOxygen['actual_loss'] = resultRatefilterInsert.apply(devByCrew, axis=1)
    #resultNitrogen['actual_loss'] = resultRateKTO.apply(devByCrew, axis=1)
    #resultWater['actual_loss'] = resultRatepretreat.apply(devByCrew, axis=1)

    resultOxygen = resultOxygen[['datedim','nasa_crew','all_crew','days_since_resupply','generation','rate_per_crew/day','rate_per_day','assumed_loss','actual_value','actual_rate_per/day']]
    resultNitrogen = resultNitrogen[['datedim','nasa_crew','all_crew','days_since_resupply','generation','rate_per_crew/day','rate_per_day','assumed_loss','actual_value','actual_rate_per/day']]
    resultWater = resultWater[['datedim','nasa_crew','all_crew','days_since_resupply','generation','rate_per_crew/day','rate_per_day','assumed_loss','actual_value','actual_rate_per/day']]

    path = os.getcwd() + "\\prediction\\predictionsCSV\\"
    resultWater.to_csv(path + 'usageRateWater.csv')
    resultNitrogen.to_csv(path + 'usageRateNitrogen.csv')
    resultOxygen.to_csv(path + 'usageRateOxygen.csv')

    return 

def calcRate(row):
    return row['rate_per_day'] + (row['rate_per_crew/day'] * row['all_crew']) - row['generation']

def calcWaterRate(row):
    return row['rate_per_day'] + (row['rate_per_crew/day'] * row['nasa_crew']) - row['generation']

def rateToNegative(row):
    if 'generation' in row['type']:
        return -1 * row['rate']
    else:
        return row['rate']
    
def subractRows1(row):
    return row['total'] - row['total1']   
  
def rateToNegative(row):
    if 'generation' in row['type']:
        return -1 * row['rate']
    else:
        return row['rate']
  
def test(startDate,endDate):
    numAll, numNASA = numCrew()
    consumablesNASA, consumablesEveryone = calculateCurrentRate()
    filterInsert,kto,pretreat,foodUS,acyInserts = compareRates()

    #turns the variables into datetime
    startDate = datetime.strptime(startDate, '%Y-%m-%d')
    endDate = datetime.strptime(endDate, '%Y-%m-%d')

    # number of days between start and end 
    numNASA.drop(numNASA[numNASA['datedim'] < startDate].index, inplace=True)
    numNASA.drop(numNASA[numNASA['datedim'] > endDate].index, inplace=True)
    numNASA = numNASA.reset_index()

    # initializes a dataframe
    result = pd.DataFrame()

    # fills the dataframe from startdate to end date
    result['datedim'] = pd.date_range(start = startDate, end = endDate)
    result["datedim"] = pd.to_datetime(result['datedim'])

    # gets the number of crew and puts it into the table also get the length
    result['crew'] = numNASA['crew_count'] 
    result['days_since_resupply'] = pd.RangeIndex(len(result.index))

    # initlialzes other tables
    resultRatefilterInsert = result.copy()
    resultRateKTO = result.copy()
    resultRatepretreat = result.copy()
    resultRatefoodUS = result.copy()
    resultRateACY = result.copy()

    resultRatefilterInsert['rate'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'Filter Inserts']["rate"].values[0]
    resultRateKTO['rate'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'KTO']["rate"].values[0]
    resultRatepretreat['rate'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'Pretreat Tanks']["rate"].values[0]
    resultRatefoodUS['rate'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'US Food BOBs']["rate"].values[0]
    resultRateACY['rate'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'ACY Inserts']["rate"].values[0]

    resultRatefilterInsert['assumed_loss'] = resultRatefilterInsert.apply(multByCrew, axis=1)
    resultRateKTO['assumed_loss'] = resultRateKTO.apply(multByCrew, axis=1)
    resultRatepretreat['assumed_loss'] = resultRatepretreat.apply(multByCrew, axis=1)
    resultRatefoodUS['assumed_loss'] = resultRatefoodUS.apply(multByCrew, axis=1)
    resultRateACY['assumed_loss'] = resultRateACY.apply(multByCrew, axis=1)

    filterInsert['quantity1'] = filterInsert['quantity']
    kto['quantity1'] = kto['quantity'] 
    pretreat['quantity1'] = pretreat['quantity'] 
    foodUS['quantity1'] = foodUS['quantity'] 
    acyInserts['quantity1'] = acyInserts['quantity']


    filterInsert['quantity1'] = filterInsert['quantity1'].shift(-1)
    kto['quantity1'] = kto['quantity1'].shift(-1)
    pretreat['quantity1'] = pretreat['quantity1'].shift(-1) 
    foodUS['quantity1'] = foodUS['quantity1'].shift(-1) 
    acyInserts['quantity1'] = acyInserts['quantity1'].shift(-1)

    filterInsert.drop(filterInsert[filterInsert['datedim'] < startDate].index, inplace=True)
    filterInsert.drop(filterInsert[filterInsert['datedim'] > endDate].index, inplace=True)
    kto.drop(kto[kto['datedim'] < startDate].index, inplace=True)
    kto.drop(kto[kto['datedim'] > endDate].index, inplace=True)
    pretreat.drop(pretreat[pretreat['datedim'] < startDate].index, inplace=True)
    pretreat.drop(pretreat[pretreat['datedim'] > endDate].index, inplace=True)
    foodUS.drop(foodUS[foodUS['datedim'] < startDate].index, inplace=True)
    foodUS.drop(foodUS[foodUS['datedim'] > endDate].index, inplace=True)
    acyInserts.drop(acyInserts[acyInserts['datedim'] < startDate].index, inplace=True)
    acyInserts.drop(acyInserts[acyInserts['datedim'] > endDate].index, inplace=True)

    filterInsert['difference'] = filterInsert.apply(subractRows, axis=1)
    kto['difference'] = kto.apply(subractRows, axis=1)
    pretreat['difference'] = pretreat.apply(subractRows, axis=1)
    foodUS['difference'] = foodUS.apply(subractRows, axis=1)
    acyInserts['difference'] = acyInserts.apply(subractRows, axis=1)

    # filterInsert['difference'] = filterInsert['calculated_volume'] - filterInsert['calculated_volume'].iloc[0]
    # kto['difference'] = kto['calculated_volume'] - kto['calculated_volume'].iloc[0]
    # pretreat['difference'] = pretreat['calculated_volume'] - pretreat['calculated_volume'].iloc[0]
    # foodUS['difference'] = foodUS['calculated_volume'] - foodUS['calculated_volume'].iloc[0]
    # acyInserts['difference'] = acyInserts['calculated_volume'] - acyInserts['calculated_volume'].iloc[0]
    
    resultRatefilterInsert['difference'] = filterInsert['difference']
    resultRateKTO['difference'] = kto['difference']
    resultRatepretreat['difference'] = pretreat['difference']
    resultRatefoodUS['difference'] = foodUS['difference']
    resultRateACY['difference'] = acyInserts['difference'] 

    resultRatefilterInsert = resultRatefilterInsert.fillna(0)
    resultRateKTO = resultRateKTO.fillna(0)
    resultRatepretreat = resultRatepretreat.fillna(0)
    resultRatefoodUS = resultRatefoodUS.fillna(0)
    resultRateACY = resultRateACY.fillna(0)
    
    resultRatefilterInsert['actual_loss'] = resultRatefilterInsert.apply(devByCrew, axis=1)
    resultRateKTO['actual_loss'] = resultRateKTO.apply(devByCrew, axis=1)
    resultRatepretreat['actual_loss'] = resultRatepretreat.apply(devByCrew, axis=1)
    resultRatefoodUS['actual_loss'] = resultRatefoodUS.apply(devByCrew, axis=1)
    resultRateACY['actual_loss'] = resultRateACY.apply(devByCrew, axis=1)

    path = os.getcwd() + "\\prediction\\predictionsCSV\\"

    resultRatefilterInsert.to_csv(path + 'usageRateFilterInsert.csv')
    resultRateKTO.to_csv(path + 'usageRateKTO.csv')
    resultRatepretreat.to_csv(path + 'usageRatePretreat.csv')
    resultRatefoodUS.to_csv(path + 'usageRateFoodUS.csv')
    resultRateACY.to_csv(path + 'usageRateACY.csv')

    return 

def multByCrew(row):
    return row['rate'] * row['crew']

def devByCrew(row):
    return (row['difference'] /row['crew'] )# / row['days_since_resupply']

def subractRows(row):
    return row['quantity'] - row['quantity1'] 

def question2(startDate):
    result = pd.DataFrame()
    filterInsert,kto,pretreat,foodUS,acyInserts = compareRates()
    numAll, numNASA = numCrew()
    consumablesNASA, filler = calculateCurrentRate()
    consumablesEveryone = calculateActualRate()

    datesOfFlights = getDropDates()
    datesOfFlights['resupply'] = 'True'

    threshold = pd.read_csv(csvPath + 'thresholdsLimits.csv')
    threshold = threshold.copy(deep=True)
    threshold.drop(threshold[threshold['threshold_owner'] == 'RSOS'].index, inplace = True)
    threshold['actual_loss'] = threshold.apply(applySafetyFactor, axis=1)

    # gets start date to datetime and also gets enddate by adding 2 years to start date
    startDate = datetime.strptime(startDate, '%Y-%m-%d')
    endDate = startDate + relativedelta(years=2)

    datesOfFlights.drop(datesOfFlights[datesOfFlights['datedim'] < startDate].index, inplace = True)
    datesOfFlights.drop(datesOfFlights[datesOfFlights['datedim'] > endDate].index, inplace = True)
    filterInsert.drop(filterInsert[filterInsert['datedim'] < startDate].index, inplace=True)
    filterInsert.drop(filterInsert[filterInsert['datedim'] > endDate].index, inplace=True)
    kto.drop(kto[kto['datedim'] < startDate].index, inplace=True)
    kto.drop(kto[kto['datedim'] > endDate].index, inplace=True)
    pretreat.drop(pretreat[pretreat['datedim'] < startDate].index, inplace=True)
    pretreat.drop(pretreat[pretreat['datedim'] > endDate].index, inplace=True)
    foodUS.drop(foodUS[foodUS['datedim'] < startDate].index, inplace=True)
    foodUS.drop(foodUS[foodUS['datedim'] > endDate].index, inplace=True)
    acyInserts.drop(acyInserts[acyInserts['datedim'] < startDate].index, inplace=True)
    acyInserts.drop(acyInserts[acyInserts['datedim'] > endDate].index, inplace=True)
    numAll.drop(numAll[numAll['datedim'] < startDate].index, inplace = True)
    numAll.drop(numAll[numAll['datedim'] > endDate].index, inplace = True)
    numAll = numAll.reset_index()
    numNASA.drop(numNASA[numNASA['datedim'] < startDate].index, inplace = True)
    numNASA.drop(numNASA[numNASA['datedim'] > endDate].index, inplace = True)
    numNASA = numNASA.reset_index()
    result['datedim'] = pd.date_range(start = startDate, end = endDate)
    result["datedim"] = pd.to_datetime(result['datedim'])

    result = pd.merge(result, datesOfFlights, on='datedim', how='left')
    result = result.fillna('False')

    result['crew_everyone'] = numAll['crew_count']
    result['crew_nasa'] = numNASA['crew_count']
    
    result['threshold_acy'] = threshold[threshold['threshold_category'] == 'ACY Insert']['actual_loss'].values[0]
    result['threshold_kto'] = threshold[threshold['threshold_category'] == 'KTO']['actual_loss'].values[0]
    result['threshold_pretreat'] = threshold[threshold['threshold_category'] == 'Pretreat Tanks']['actual_loss'].values[0]
    result['threshold_filter'] = threshold[threshold['threshold_category'] == 'Filter Inserts']['actual_loss'].values[0]
    result['threshold_food_us'] = threshold[threshold['threshold_category'] == 'Food']['actual_loss'].values[0]

    result['rate_filter'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'Filter Inserts']["rate"].values[0]
    result['rate_kto'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'KTO']["rate"].values[0]
    result['rate_pretreat'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'Pretreat Tanks']["rate"].values[0]
    result['rate_acy'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'ACY Inserts']["rate"].values[0]
    result['rate_food_us'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'US Food BOBs']["rate"].values[0]

    result['assumed_loss_filter'] = result.apply(multByCrew1, axis=1,rate='rate_filter')
    result['assumed_loss_kto'] = result.apply(multByCrew1, axis=1,rate='rate_kto')
    result['assumed_loss_pretreat'] = result.apply(multByCrew1, axis=1,rate='rate_pretreat')
    result['assumed_loss_acy'] = result.apply(multByCrew1, axis=1,rate='rate_acy')
    result['assumed_loss_food_us'] = result.apply(multByCrew1, axis=1,rate='rate_food_us')

    result['total_filter'] = iteration(result,filterInsert[filterInsert['datedim'] == startDate]["quantity"].values[0],"assumed_loss_filter")
    result['total_kto'] = iteration(result,kto[kto['datedim'] == startDate]["quantity"].values[0],"assumed_loss_kto")
    result['total_pretreat'] = iteration(result,pretreat[pretreat['datedim'] == startDate]["quantity"].values[0],"assumed_loss_pretreat")
    result['total_acy'] = iteration(result,acyInserts[acyInserts['datedim'] == startDate]["quantity"].values[0],"assumed_loss_acy")
    result['total_food_us'] = iteration(result,foodUS[foodUS['datedim'] == startDate]["quantity"].values[0],"assumed_loss_food_us")
    
    result.drop(result[result['resupply'] == 'False'].index, inplace=True)
    result['temp'] = result['datedim'].shift(-1)
    result['days_between_mission'] = (result['temp'] - result['datedim']).dt.days
    result.drop(['temp'],axis = 1,inplace=True)
    result.reset_index(drop=True, inplace=True)

    result['resupply_needed_filter'],result['current_filter'] = calculateResupply(result,"threshold_filter","total_filter")
    result['resupply_needed_kto'],result['current_kto'] = calculateResupply(result,"threshold_kto","total_kto")
    result['resupply_needed_pretreat'],result['current_pretreat'] = calculateResupply(result,"threshold_pretreat","total_pretreat")
    result['resupply_needed_acy'],result['current_acy'] = calculateResupply(result,"threshold_acy","total_acy")
    result['resupply_needed_food_us'],result['current_food_us'] = calculateResupply(result,"threshold_food_us","total_food_us")

    path = os.getcwd() + "\\prediction\\predictionsCSV\\"

    finalFilter = result[['datedim','resupply_needed_filter','current_filter']]
    finalKTO = result[['datedim','resupply_needed_kto','current_kto']]
    finalPretreat = result[['datedim','resupply_needed_pretreat','current_pretreat']]
    finalACY = result[['datedim','resupply_needed_acy','current_acy']]
    finalFoodUS = result[['datedim','resupply_needed_food_us','current_food_us']]

    finalFilter.to_csv(path + 'finalFilter.csv')
    finalKTO.to_csv(path + 'finalKTO.csv')
    finalPretreat.to_csv(path + 'finalPretreat.csv')
    finalACY.to_csv(path + 'finalACY.csv')
    finalFoodUS.to_csv(path + 'finalFoodUS.csv')

    return


def iteration(data,cur,assumedLoss):
    result = []
    for index, row in data.iterrows():
        cur -= row[assumedLoss]
        result.append(cur)
    return result

def calculateResupply(data, threshold, total):
    result = []
    current_total = []
    data['temp'] = data[total] - data[total].shift(-1).fillna(0)  # Handle NaN for the last row
    current = data[total].values[0]
    for index, row in data.iterrows():
        current -= row['temp']  # Update current with consumption
        if current < row[threshold]:
            resupply_needed = row[threshold] - current  # Calculate resupply needed
            current = row[threshold]  # Update current to reflect resupply
            result.append(resupply_needed)
        else:
            result.append(0)
        current_total.append(current)
    
    data.drop(['temp'], axis=1, inplace=True)
    return result,current_total


def multByCrew1(row,rate):
    return row['crew_nasa'] * row[rate]

def applySafetyFactor(row):
    return (row['threshold_value'] * 0.10) + row['threshold_value']

def question2a(startDate):
    result = pd.DataFrame()
    oxygen, nitrogen= getOxygenNitrogen()
    water = getFilledWaterData()
    numAll, numNASA = numCrew()
    consumablesNASA, filler = calculateCurrentRate()
    consumablesEveryone = calculateActualRate()

    water = water.set_index('datedim').resample('D').ffill().reset_index()
    oxygen = oxygen.set_index('datedim').resample('D').ffill().reset_index()
    nitrogen = nitrogen.set_index('datedim').resample('D').ffill().reset_index()

    datesOfFlights = getDropDates()
    datesOfFlights['resupply'] = 'True' 

    threshold = pd.read_csv(csvPath + 'thresholdsLimits.csv')
    threshold = threshold.copy(deep=True)
    threshold.drop(threshold[threshold['threshold_owner'] == 'RSOS'].index, inplace = True)
    threshold['actual_loss'] = threshold.apply(applySafetyFactor, axis=1)

    # gets start date to datetime and also gets enddate by adding 2 years to start date
    startDate = datetime.strptime(startDate, '%Y-%m-%d')
    endDate = startDate + relativedelta(years=2)

    datesOfFlights.drop(datesOfFlights[datesOfFlights['datedim'] < startDate].index, inplace = True)
    datesOfFlights.drop(datesOfFlights[datesOfFlights['datedim'] > endDate].index, inplace = True)
    oxygen.drop(oxygen[oxygen['datedim'] < startDate].index, inplace=True)
    oxygen.drop(oxygen[oxygen['datedim'] > endDate].index, inplace=True)
    nitrogen.drop(nitrogen[nitrogen['datedim'] < startDate].index, inplace=True)
    nitrogen.drop(nitrogen[nitrogen['datedim'] > endDate].index, inplace=True)
    water.drop(water[water['datedim'] < startDate].index, inplace=True)
    water.drop(water[water['datedim'] > endDate].index, inplace=True)
    numAll.drop(numAll[numAll['datedim'] < startDate].index, inplace = True)
    numAll.drop(numAll[numAll['datedim'] > endDate].index, inplace = True)
    numAll = numAll.reset_index()
    numNASA.drop(numNASA[numNASA['datedim'] < startDate].index, inplace = True)
    numNASA.drop(numNASA[numNASA['datedim'] > endDate].index, inplace = True)
    numNASA = numNASA.reset_index()

    result['datedim'] = pd.date_range(start = startDate, end = endDate)
    result["datedim"] = pd.to_datetime(result['datedim'])

    result = pd.merge(result, datesOfFlights, on='datedim', how='left')
    result = result.fillna('False')

    result['crew_everyone'] = numAll['crew_count']
    result['crew_nasa'] = numNASA['crew_count']

    result['threshold_oxygen'] = threshold[threshold['threshold_category'] == 'O2 (Oxygen)']['actual_loss'].values[0] * 0.45359237 # lbs to kG
    result['threshold_water'] = threshold[threshold['threshold_category'] == 'Water Alert']['actual_loss'].values[0]
    result['threshold_nitrogen'] = threshold[threshold['threshold_category'] == 'N2 (Nitrogen)']['actual_loss'].values[0] * 0.45359237 # lbs to kG

    result['generation_oxygen'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Oxygen']["generation"].values[0]
    result['generation_water'] = (consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Water']["generation"].values[0] / 2) # maybe need to change this
    result['generation_nitrogen'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Nitrogen']["generation"].values[0]

    result['rate_crew_oxygen'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Oxygen']["rate_per_crew/day"].values[0]
    result['rate_crew_water'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Water']["rate_per_crew/day"].values[0]
    result['rate_crew_nitrogen'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Nitrogen']["rate_per_crew/day"].values[0]

    result['rate_day_oxygen'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Oxygen']["rate_per_day"].values[0]
    result['rate_day_water'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Water']["rate_per_day"].values[0]
    result['rate_day_nitrogen'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Nitrogen']["rate_per_day"].values[0]

    result['actual_rate_loss_oxygen'] = result.apply(calcRate1, axis=1, day = 'rate_day_oxygen', crew = 'rate_crew_oxygen', generation = 'generation_oxygen')
    result['actual_rate_loss_nitrogen'] = result.apply(calcRate1, axis=1, day = 'rate_day_nitrogen', crew = 'rate_day_nitrogen', generation = 'rate_day_nitrogen')
    result['actual_rate_loss_water'] = result.apply(calcWaterRate1, axis=1, day = 'rate_day_water', crew = 'rate_crew_water', generation = 'generation_water')

    result['total_oxygen'] = iteration(result,oxygen[oxygen['datedim'] == startDate]["total"].values[0],"actual_rate_loss_oxygen")
    result['total_nitrogen'] = iteration(result,nitrogen[nitrogen['datedim'] == startDate]["total"].values[0],"actual_rate_loss_nitrogen")
    result['total_water'] = iteration(result,water[water['datedim'] == startDate]["total"].values[0],"actual_rate_loss_water")

    result.drop(result[result['resupply'] == 'False'].index, inplace=True)
    result['temp'] = result['datedim'].shift(-1)
    result['days_between_mission'] = (result['temp'] - result['datedim']).dt.days
    result.drop(['temp'],axis = 1,inplace=True)
    result = result.reset_index()

    result['period_loss_oxygen'] = result['total_oxygen'] - result['total_oxygen'].shift(-1).fillna(0)
    result['period_loss_nitrogen'] = result['total_nitrogen'] - result['total_nitrogen'].shift(-1).fillna(0)
    result['period_loss_water'] = result['total_water'] - result['total_water'].shift(-1).fillna(0)

    result['resupply_needed_oxygen'] , result['current_oxygen'] = calculateResupply(result,"threshold_oxygen","total_oxygen")
    result['resupply_needed_nitrogen'] , result['current_nitrogen'] = calculateResupply(result,"threshold_nitrogen","total_nitrogen")
    result['resupply_needed_water'], result['current_water'] = calculateResupply(result,"threshold_water","total_water")

    finalOxygen = result[['datedim','resupply_needed_oxygen','current_oxygen']]
    finalNitrogen = result[['datedim','resupply_needed_nitrogen','current_nitrogen']]
    finalWater = result[['datedim','resupply_needed_water','current_water']]

    path = os.getcwd() + "\\prediction\\predictionsCSV\\"

    finalOxygen.to_csv(path + 'resultOxygen.csv')
    finalNitrogen.to_csv(path + 'resultNitrogen.csv')
    finalWater.to_csv(path + 'resultWater.csv')

    return result

def calcRate1(row,day,crew,generation):
    return row[day] + (row[crew] * row['crew_everyone']) - row[generation]

def calcWaterRate1(row,day,crew,generation):
    return row[day] + (row[crew] * row['crew_nasa']) - row[generation]

def question4():
    path = (os.getcwd() +"/prediction/predictionsCSV/")

    data = pd.read_csv(path + 'resultWater.csv')
    water = data.copy(deep=True)

    data = pd.read_csv(path + 'resultOxygen.csv')
    oxygen = data.copy(deep=True)

    data = pd.read_csv(path + 'resultNitrogen.csv')
    nitrogen = data.copy(deep=True)

    data = pd.read_csv(path + 'finalPretreat.csv')
    pretreat = data.copy(deep=True)

    data = pd.read_csv(path + 'finalKTO.csv')
    kto = data.copy(deep=True)

    data = pd.read_csv(path + 'finalFoodUS.csv')
    food = data.copy(deep=True)

    data = pd.read_csv(path + 'finalFilter.csv')
    filter = data.copy(deep=True)

    data = pd.read_csv(path + 'finalACY.csv')
    acy = data.copy(deep=True)

    water = water[['datedim','resupply_needed_water']]
    oxygen = oxygen[['datedim','resupply_needed_oxygen']]
    nitrogen = nitrogen[['datedim','resupply_needed_nitrogen']]
    pretreat = pretreat[['datedim','resupply_needed_pretreat']]
    kto = kto[['datedim','resupply_needed_kto']]
    food = food[['datedim','resupply_needed_food_us']]
    filter = filter[['datedim','resupply_needed_filter']]
    acy = acy[['datedim','resupply_needed_acy']]

    result = pd.merge(water,oxygen,on='datedim',how='outer')
    result = pd.merge(result,nitrogen,on='datedim',how='outer')
    result = pd.merge(result,pretreat,on='datedim',how='outer')
    result = pd.merge(result,kto,on='datedim',how='outer')
    result = pd.merge(result,food,on='datedim',how='outer')
    result = pd.merge(result,filter,on='datedim',how='outer')
    result = pd.merge(result,acy,on='datedim',how='outer')

    cols = ['resupply_needed_water','resupply_needed_oxygen','resupply_needed_nitrogen','resupply_needed_pretreat','resupply_needed_kto','resupply_needed_food_us','resupply_needed_filter', 'resupply_needed_acy']
    result['sum'] = result[cols].sum(axis=1)

    result['datedim'] = pd.to_datetime(result['datedim'])
    
    random = result.loc[result['sum'].idxmax()]
    q4 = pd.DataFrame(random)

    maxes = result.set_index('datedim')
    maxes = maxes.drop(columns='sum')
    maxes = maxes.apply(pd.Series.nlargest, n=5).unstack().dropna()
    maxes = pd.DataFrame(maxes)
    
    maxes.rename(columns={0: 'Total'}, inplace=True)
    maxes.sort_values('Total',ascending=False, inplace=True)
    
    q4.rename({'sum': 'Total Cargo Needed(kg)'}, inplace=True)
    q4.rename(columns={17: 'Total'}, inplace=True)

    path = os.getcwd() + "\\prediction\\predictionsCSV\\"

    q4.to_csv(path + 'predictionQ4.csv')
    maxes.to_csv(path + 'predictionTop5.csv')

    return
  
# test('2022-03-03','2023-01-01')
# test2('2022-03-03','2023-01-01')
#question2('2023-08-25')
#question2a('2023-08-25')
question4()


