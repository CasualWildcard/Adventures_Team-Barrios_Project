import datetime
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta 
import os

# while most of these variable names are not good I know but they are something :)
# most 

csvPath = (os.getcwd() +"/back-end/csvStorage/") # get the directory in which to pull the csv's from

def getDropDates(): # this is done
    data = pd.read_csv(csvPath + 'issFlightPlan.csv') # get the data
    data = data.copy(deep=True) # copies the data
    data.drop(data[data['event'] != "Dock"].index, inplace = True) # drops rows that does not have Dock in their event column

    # will use this to list to drop the ones that does not have this in the column of  
    words = ['NG', 'SpX', 'Progress', 'Ax', 'HTV-X']

    # Create a boolean mask where True indicates the rows to be dropped
    mask = data['vehicle_name'].str.contains('|'.join(words))

    # keep rows that contain the words
    data = data[mask]

    data = data[["datedim"]] # only gets the datedim column
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
    # gets the consumables csv & stored comsumables
    consumables = pd.read_csv(csvPath + 'consumables.csv')
    storedConsumables = pd.read_csv(csvPath + 'storedItemsOnlyIMS.csv')
    consumables = consumables.copy(deep=True)
    storedConsumables = storedConsumables.copy(deep=True)

    # puts this into datetime because it does not match the formatting of the consumables column
    storedConsumables['datedim'] = pd.to_datetime(storedConsumables['datedim'])

    # since this data set does not have headers currently will place the headers with this :)
    consumables.columns =['datedim','id','id_parent','id_path','tree_depth','tree','part_number','serial_number','location_name','original_ip_owner','current_ip_owner','operational_nomenclature','russian_name','english_name','barcode','quantity','width','height','length','diameter','calculated_volume','stwg_ovrrd_vol','children_volume','stwg_ovrrd_chldren_vol','ovrrd_notes','volume_notes','expire_date','launch','type','hazard','state','status','is_container','is_moveable','system','subsystem','action_date','move_date','fill_status','categoryID','category_name']
    
    # merges the data set both together
    consumables = pd.concat([consumables,storedConsumables])
    
    # Making sure that the ownder is NASA - Maybe this will need to be deleted or there may be some other columns that this can be done like
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

    # just grabs these columns 
    water = water[['Date', 'Corrected Total (L)']]
    water['Date'] = pd.to_datetime(water['Date'])
    # renames the column to match format in the acutal prediction model
    water.rename({'Date': 'datedim','Corrected Total (L)' : 'total'}, axis=1, inplace=True)
    return water


def getOxygenNitrogen():
    data = pd.read_csv(csvPath + 'weeklyGasSummary.csv')
    data = data.copy(deep=True)

    data = data[['Date','Adjusted O2 (kg)','Adjusted N2 (kg)']]
    #turns date into datetime to be much more managable and be compared to the other data sets 
    data['Date'] = pd.to_datetime(data['Date'])

    # cuts it and renames columns
    oxygen = data[['Date','Adjusted O2 (kg)']]
    nitrogen = data[['Date','Adjusted N2 (kg)']]
    oxygen.rename({'Date': 'datedim','Adjusted O2 (kg)' : 'total'}, axis=1, inplace=True)
    nitrogen.rename({'Date': 'datedim','Adjusted N2 (kg)' : 'total'}, axis=1, inplace=True)
    return oxygen, nitrogen

def compareRates():
    dates = getDropDates()
    consumables = modifyConsumables()

    #will cut the consumables into the different category based on the test_ims category lookup
    
    # will take the only take the ones that has the category_name filter inserts etc
    # then it will sum the quantities based on the date for example there are multiple rows with the date 2022-10-10 it will sum the quantities on those and 
    # it will be the total for that day
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
    data = pd.read_csv(csvPath + 'ratesDefinition.csv') # gets the rates definition
    data = data.copy(deep=True)
    
    # groups them into a much more managable data types since one is for the big data and the rest is for everyone
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
                                     (data['affected_consumable'] == 'Water')].index)
    # drops the russian rates definitions
    consumablesEveryone = consumablesEveryone.drop(consumablesEveryone[(consumablesEveryone['rate_category'] == 'RSOS Crew Water Consumption (Food/Drinking)') | 
                                                                        (consumablesEveryone['rate_category'] == 'RSOS Condensate Processed to Potable')].index)
    
    consumablesEveryone = consumablesEveryone[['affected_consumable','rate','units','type']] # we only need these columns

    consumablesNASA = consumablesNASA[['affected_consumable','rate']] # we only need these columns

    return consumablesNASA, consumablesEveryone

def numCrew():
    crew = pd.read_csv(csvPath + 'issFlightPlanCrew.csv')
    crew = crew.copy(deep=True)

    # crew without russians based on one csvs
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
    # Retrieve current rates for NASA and everyone else from a predefined function
    consumablesNASA, consumablesEveryone = calculateCurrentRate()
    actual = pd.DataFrame()

    # Aggregate generation rates by consumable type
    # 'generation' type data is summed for each consumable
    temp = consumablesEveryone[consumablesEveryone['type'] == 'generation']
    temp = temp.groupby("affected_consumable", as_index=False).sum(numeric_only=True)[['rate', 'affected_consumable']]
    temp = temp.rename(columns={"rate": "generation"})

    # Aggregate rates per crew/day by consumable
    # Filters data by units containing 'Crew' and sums the rates for each consumable
    temp1 = consumablesEveryone[consumablesEveryone['units'].str.contains('Crew', case=False)]
    temp1 = temp1.groupby("affected_consumable", as_index=False).sum(numeric_only=True)[['rate', 'affected_consumable']]
    temp1 = temp1.rename(columns={"rate": "rate_per_crew/day"})

    # Remove rows with 'generation' type and 'Crew' in the 'units' column from consumablesEveryone
    consumablesEveryone.drop(consumablesEveryone[consumablesEveryone['type'] == 'generation'].index, inplace=True)
    consumablesEveryone = consumablesEveryone[~consumablesEveryone['units'].str.contains('Crew', case=False)]
    consumablesEveryone = consumablesEveryone.groupby("affected_consumable", as_index=False).sum(numeric_only=True)[['rate', 'affected_consumable']]
    consumablesEveryone = consumablesEveryone.rename(columns={"rate": "rate_per_day"})

    # Combine the three datasets (temp, temp1, consumablesEveryone) into one
    # This results in a DataFrame with rates for each consumable, including generation rate, rate per crew/day, and overall rate per day
    actual = pd.merge(temp, temp1, on="affected_consumable", how="outer")
    actual = pd.merge(actual, consumablesEveryone, on="affected_consumable", how="outer")
    actual = actual.fillna(0)
    actual.reset_index(drop=True, inplace=True)

    return actual

    
def Q1Shared(startDate,endDate): # question 1 for oxygen nitrogen and water
    numAll, numNASA = numCrew()
    consumablesEveryone = calculateActualRate()
    oxygen, nitrogen= getOxygenNitrogen()
    water = getFilledWaterData()

    #turns the variables into datetime
    startDate = datetime.strptime(startDate, '%Y-%m-%d')
    endDate = datetime.strptime(endDate, '%Y-%m-%d')

    # will drop the days that is not between the start date and the end date
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

    # since oxygen and nitrogen has the same date this is done for both of them 
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

    # only for the water because the dates are different 
    # Merge with left join to keep only the rows with corresponding dates in water
    merged_data = pd.merge(result1, water, on='datedim', how='left')

    # Filter out rows where 'total' is not null (indicating a match with the water DataFrame)
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

    # now for each result we get the rates and generation and put it into a column it will be the same number we will do some calculations to acutally 
    # get the predicted use
    resultOxygen['generation'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Oxygen']["generation"].values[0]
    resultNitrogen['generation'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Water']["generation"].values[0]
    resultWater['generation'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Nitrogen']["generation"].values[0]

    resultOxygen['rate_per_crew/day'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Oxygen']["rate_per_crew/day"].values[0]
    resultNitrogen['rate_per_crew/day'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Water']["rate_per_crew/day"].values[0]
    resultWater['rate_per_crew/day'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Nitrogen']["rate_per_crew/day"].values[0]

    resultOxygen['rate_per_day'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Oxygen']["rate_per_day"].values[0]
    resultNitrogen['rate_per_day'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Water']["rate_per_day"].values[0]
    resultWater['rate_per_day'] = consumablesEveryone[consumablesEveryone['affected_consumable'] == 'Nitrogen']["rate_per_day"].values[0]

    # this is how you will be able to calculate the assumed/predicted loss 
    resultOxygen['assumed_loss'] = resultOxygen.apply(calcRate, axis=1)
    resultNitrogen['assumed_loss'] = resultNitrogen.apply(calcRate, axis=1)
    resultWater['assumed_loss'] = resultWater.apply(calcWaterRate, axis=1)

    # actual values meaning the acutal total/calculated volume of these
    resultOxygen['actual_value'] = oxygen['total']
    resultNitrogen['actual_value'] = nitrogen['total'] 
    resultWater['actual_value'] = water['total'] 

    # This multiple lines of code will calculate the difference between total now - total tommorrow(in water oxygen and nitrogens case next week)
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

    # this can be use to calculate the difference by the top calculated volume - calculated_volume[x] then putting it into a column
    # oxygen['difference'] = oxygen['calculated_volume'] - oxygen['calculated_volume'].iloc[0]
    # nitrogen['difference'] = nitrogen['calculated_volume'] - nitrogen['calculated_volume'].iloc[0]
    # water['difference'] = water['calculated_volume'] - water['calculated_volume'].iloc[0]
    
    resultOxygen['actual_rate_per/day'] = oxygen['difference']
    resultNitrogen['actual_rate_per/day'] = nitrogen['difference']
    resultWater['actual_rate_per/day'] = water['difference']

    # if there were calculations needed will fill the NANs with 0
    #resultOxygen = resultOxygen.fillna(0)
    #resultNitrogen = resultNitrogen.fillna(0)
    #resultWater = resultWater.fillna(0)

    #gets these columns
    resultOxygen = resultOxygen[['datedim','nasa_crew','all_crew','days_since_resupply','generation','rate_per_crew/day','rate_per_day','assumed_loss','actual_value','actual_rate_per/day']]
    resultNitrogen = resultNitrogen[['datedim','nasa_crew','all_crew','days_since_resupply','generation','rate_per_crew/day','rate_per_day','assumed_loss','actual_value','actual_rate_per/day']]
    resultWater = resultWater[['datedim','nasa_crew','all_crew','days_since_resupply','generation','rate_per_crew/day','rate_per_day','assumed_loss','actual_value','actual_rate_per/day']]
    
    # turns the results into csv and puts it into a folder for front end to use
    path = os.getcwd() + "\\prediction\\predictionsCSV\\"
    resultWater.to_csv(path + 'usageRateWater.csv')
    resultNitrogen.to_csv(path + 'usageRateNitrogen.csv')
    resultOxygen.to_csv(path + 'usageRateOxygen.csv')

    return 

# calculate the actuall loss is based on crew count and rates with generation subtracts from the total and if some of them are 0 then it will only use rate per day
def calcRate(row):
    return row['rate_per_day'] + (row['rate_per_crew/day'] * row['all_crew']) - row['generation']

def calcWaterRate(row):
    return row['rate_per_day'] + (row['rate_per_crew/day'] * row['nasa_crew']) - row['generation']

# caculate the difference of today - tomorrow
def subractRows1(row):
    return row['total'] - row['total1']   
  
  
def Q1Consumables(startDate,endDate): # question 1 but for the consumables
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

    # gets the rate of the consumable 
    resultRatefilterInsert['rate'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'Filter Inserts']["rate"].values[0]
    resultRateKTO['rate'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'KTO']["rate"].values[0]
    resultRatepretreat['rate'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'Pretreat Tanks']["rate"].values[0]
    resultRatefoodUS['rate'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'US Food BOBs']["rate"].values[0]
    resultRateACY['rate'] = consumablesNASA[consumablesNASA['affected_consumable'] == 'ACY Inserts']["rate"].values[0]

    # gets the assumed loss since consumables are only crew/day no need to get generation or per/day
    # rate * the number of nasa side astraunout that day
    resultRatefilterInsert['assumed_loss'] = resultRatefilterInsert.apply(multByCrew, axis=1)
    resultRateKTO['assumed_loss'] = resultRateKTO.apply(multByCrew, axis=1)
    resultRatepretreat['assumed_loss'] = resultRatepretreat.apply(multByCrew, axis=1)
    resultRatefoodUS['assumed_loss'] = resultRatefoodUS.apply(multByCrew, axis=1)
    resultRateACY['assumed_loss'] = resultRateACY.apply(multByCrew, axis=1)

    # does the same thing as the other # This multiple lines of code will calculate the difference between total now - total tommorrow
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

    # need to fill na because we are dividing by the number of crew
    resultRatefilterInsert = resultRatefilterInsert.fillna(0)
    resultRateKTO = resultRateKTO.fillna(0)
    resultRatepretreat = resultRatepretreat.fillna(0)
    resultRatefoodUS = resultRatefoodUS.fillna(0)
    resultRateACY = resultRateACY.fillna(0)
    
    # acutal loss is rate per crew/day
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

# mult crew only at nasa's side and the rate it will get the assumed loss
def multByCrew(row):
    return row['rate'] * row['crew']

# rate per crew per day
def devByCrew(row):
    return (row['difference'] /row['crew'] )# / row['days_since_resupply']

def subractRows(row):
    return row['quantity'] - row['quantity1'] 

def Q2Consumables(startDate): # question 2 for consumables
    result = pd.DataFrame()
    filterInsert,kto,pretreat,foodUS,acyInserts = compareRates()
    numAll, numNASA = numCrew()
    consumablesNASA, filler = calculateCurrentRate()
    consumablesEveryone = calculateActualRate()

    # the ressuply column is for future actions since we need to keep track of when the dates that they ressuply and we need to merge this with the
    # consumables to have false if there is not ressuply and true if there is
    datesOfFlights = getDropDates()
    datesOfFlights['resupply'] = 'True'

    # gets the threshold and drops the RSOS and applies the 10% safety factor
    threshold = pd.read_csv(csvPath + 'thresholdsLimits.csv')
    threshold = threshold.copy(deep=True)
    threshold.drop(threshold[threshold['threshold_owner'] == 'RSOS'].index, inplace = True)
    threshold['actual_loss'] = threshold.apply(applySafetyFactor, axis=1)

    # gets start date to datetime and also gets enddate by adding 2 years to start date
    startDate = datetime.strptime(startDate, '%Y-%m-%d')
    endDate = startDate + relativedelta(years=2)

    # cuts the data between the start date and the end date
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

    # now to start the template I put all the data needed into result and will just drop the column not needed for each consumables at the end
    result['datedim'] = pd.date_range(start = startDate, end = endDate)
    result["datedim"] = pd.to_datetime(result['datedim'])

    # this is the part where I merge the drop dates and put false if there is no ressuply during this day
    result = pd.merge(result, datesOfFlights, on='datedim', how='left')
    result = result.fillna('False')

    # gets the information needed like consumables number of crew and the consumables and also the rate
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

    # will find the assumed loss of the data
    result['assumed_loss_filter'] = result.apply(multByCrew1, axis=1,rate='rate_filter')
    result['assumed_loss_kto'] = result.apply(multByCrew1, axis=1,rate='rate_kto')
    result['assumed_loss_pretreat'] = result.apply(multByCrew1, axis=1,rate='rate_pretreat')
    result['assumed_loss_acy'] = result.apply(multByCrew1, axis=1,rate='rate_acy')
    result['assumed_loss_food_us'] = result.apply(multByCrew1, axis=1,rate='rate_food_us')

    # the filterInsert[filterInsert['datedim'] == startDate]["quantity"].values[0] will get the total quantity of filter insert during the start date lets call this x
    # then it will do subtraction based on the x - the assumed loss during that day and will put it into a list then do the same calculation again with the result 
    # of the subtraction and the next assummed loss it will do this until the end of the rows
    # will then turn the list into a column total
    result['total_filter'] = iteration(result,filterInsert[filterInsert['datedim'] == startDate]["quantity"].values[0],"assumed_loss_filter")
    result['total_kto'] = iteration(result,kto[kto['datedim'] == startDate]["quantity"].values[0],"assumed_loss_kto")
    result['total_pretreat'] = iteration(result,pretreat[pretreat['datedim'] == startDate]["quantity"].values[0],"assumed_loss_pretreat")
    result['total_acy'] = iteration(result,acyInserts[acyInserts['datedim'] == startDate]["quantity"].values[0],"assumed_loss_acy")
    result['total_food_us'] = iteration(result,foodUS[foodUS['datedim'] == startDate]["quantity"].values[0],"assumed_loss_food_us")
    
    # Now this will drop the non ressuply dates
    result.drop(result[result['resupply'] == 'False'].index, inplace=True)

    # calculates the days between mission and resets the index for future calculations
    result['temp'] = result['datedim'].shift(-1)
    result['days_between_mission'] = (result['temp'] - result['datedim']).dt.days
    result.drop(['temp'],axis = 1,inplace=True)
    result.reset_index(drop=True, inplace=True)

    # alright the most complicated part of all of the code
    # to explain this i have now the data to calculate the assumed ressuply needed
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
    data['temp'] = data[total] - data[total].shift(-1).fillna(0)  # subtract total from total next mission date
    current = data[total].values[0] # we get the first missions supply with this 
    for index, row in data.iterrows():
        current -= row['temp']  # Update current with consumption
        if current < row[threshold]: # if it is below threshold then 
            resupply_needed = row[threshold] - current  # Calculate resupply needed
            current = row[threshold]  # Update current to reflect resupply
            result.append(resupply_needed) # append supply needed for a row
        else:
            result.append(0) # otherwise we do not need supplies
        current_total.append(current)
    
    data.drop(['temp'], axis=1, inplace=True)
    return result,current_total

# will find the assumed loss of the data
def multByCrew1(row,rate):
    return row['crew_nasa'] * row[rate]

def applySafetyFactor(row):
    return (row['threshold_value'] * 0.10) + row['threshold_value']

def Q2Shared(startDate): # question 2 water, nitrogen and oxygen does the same thing but with minor differences
    result = pd.DataFrame()
    oxygen, nitrogen= getOxygenNitrogen()
    water = getFilledWaterData()
    numAll, numNASA = numCrew()
    consumablesNASA, filler = calculateCurrentRate()
    consumablesEveryone = calculateActualRate()

    # alrigh these data sets are for every week this will make it so that it will fill the days in between with the missions with the most recent missions and so on
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

def Q3Q4():
    path = (os.getcwd() +"/prediction/predictionsCSV/")

    # Load various CSV files related to different consumables into dataframes.
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

    # Extract only the date and resupply needed columns for further analysis.
    water = water[['datedim','resupply_needed_water']]
    oxygen = oxygen[['datedim','resupply_needed_oxygen']]
    nitrogen = nitrogen[['datedim','resupply_needed_nitrogen']]
    pretreat = pretreat[['datedim','resupply_needed_pretreat']]
    kto = kto[['datedim','resupply_needed_kto']]
    food = food[['datedim','resupply_needed_food_us']]
    filter = filter[['datedim','resupply_needed_filter']]
    acy = acy[['datedim','resupply_needed_acy']]

    # Merge all the consumables data on the 'datedim' column to consolidate the data.
    result = pd.merge(water,oxygen,on='datedim',how='outer')
    result = pd.merge(result,nitrogen,on='datedim',how='outer')
    result = pd.merge(result,pretreat,on='datedim',how='outer')
    result = pd.merge(result,kto,on='datedim',how='outer')
    result = pd.merge(result,food,on='datedim',how='outer')
    result = pd.merge(result,filter,on='datedim',how='outer')
    result = pd.merge(result,acy,on='datedim',how='outer')

    # Calculate the sum of resupply needs across all consumables for each date.
    cols = ['resupply_needed_water','resupply_needed_oxygen','resupply_needed_nitrogen','resupply_needed_pretreat','resupply_needed_kto','resupply_needed_food_us','resupply_needed_filter', 'resupply_needed_acy']
    result['sum'] = result[cols].sum(axis=1)

    # Convert the 'datedim' column to datetime format.
    result['datedim'] = pd.to_datetime(result['datedim'])
    
    # Identify the date with the maximum total resupply need.
    random = result.loc[result['sum'].idxmax()]
    q4 = pd.DataFrame(random)

    # Determine the top 5 largest needs for each consumable across all dates.
    maxes = result.set_index('datedim')
    maxes = maxes.drop(columns='sum')
    maxes = maxes.apply(pd.Series.nlargest, n=5).unstack().dropna()
    maxes = pd.DataFrame(maxes)
    
    maxes.rename(columns={0: 'Total'}, inplace=True)
    maxes.sort_values('Total',ascending=False, inplace=True)
    # Rename a column for clarity in the q4 dataframe.
    q4.rename({'sum': 'Total Cargo Needed(kg)'}, inplace=True)
    q4.rename(columns={17: 'Total'}, inplace=True)

    path = os.getcwd() + "\\prediction\\predictionsCSV\\"
    # Save the analyzed data to CSV files for reporting or further analysis.
    q4.to_csv(path + 'predictionQ4.csv')
    maxes.to_csv(path + 'predictionTop5.csv')

    return
  
Q1Consumables('2022-11-27','2023-02-11')
Q1Shared('2022-11-27','2023-02-11')
Q2Consumables('2023-08-25')
Q2Shared('2023-08-25')
Q3Q4()