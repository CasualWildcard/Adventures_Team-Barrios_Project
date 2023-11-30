def getDropDatesTwoYears():

    data = pd.read_csv('/content/drive/Shareddrives/CS 4306 Barrios Project/csv Files/iss_flight_plan_20220101-20251231.csv') # change this to where the data is going to be imported
    data = data.copy(deep=True) # copies the data
    data.drop(data[data['event'] != "Dock"].index, inplace = True) # drops rows that does not have Dock in their event column
    data = data[["datedim"]] # gets just the datedim colun and puts it into data
    data["datedim"] = pd.to_datetime(data['datedim']) # turns datedim column to an actual datedim variable to be easily comparable in the next couple of commands
    data.reset_index(drop=True) # resets the index just in case

    # drop the some data so that the time frame is just within two years
    data.drop(data[data['datedim'] >= '2025-9-6'].index, inplace = True) 
    data.drop(data[data['datedim'] <= '2023-9-6'].index, inplace = True) 

    return data


def ressuplyQuantities(data,type):
    # get number of missions within 2 years
    dates = getDropDatesTwoYears()
    rates = calculateCurrentRate()
    threshold = getThresholdLimit()
    
    # not going to worry about oxygen water and n2 for now
    # NEED TO ACCOUNT FOR 10% SAFETY FACTOR Later update getThresholdLimit()
    # dictionary name : thresholdValue rates :)
    information = {
    'ACY Insert' : [int(threshold[threshold['threshold_category'] == 'ACY Insert']['threshold_value']),int(rates[rates['affected_consumable'] == 'ACY Inserts']['rate'])],
    'KTO' : [int(threshold[threshold['threshold_category'] == 'KTO']['threshold_value']),int(rates[rates['affected_consumable'] == 'KTO']['rate'])],
    'Pretreat_Tanks' : [int(threshold[threshold['threshold_category'] == 'Pretreat Tanks']['threshold_value']),int(rates[rates['affected_consumable'] == 'Pretreat Tanks']['rate'])],
    'Filter_Inserts' : [int(threshold[threshold['threshold_category'] == 'Filter Inserts']['threshold_value']),int(rates[rates['affected_consumable'] == 'Filter Inserts']['rate'])],
    'Urine_Receptacle' : [int(threshold[threshold['threshold_category'] == 'Urine Receptacle']['threshold_value']),int(rates[rates['affected_consumable'] == 'Urine Receptacle']['rate'])],
    #'EDVs' : [int(threshold[threshold['threshold_category'] == 'EDVs']['threshold_value']), int(rates[rates['affected_consumable'] == 'asd']['rate'])],
    # Food has no threshold value :) and EDV does not have any rate of consumptions 
    'Nitrogen' : [int(threshold[threshold['threshold_category'] == 'N2 (Nitrogen)']['threshold_value']),int(rates[rates['affected_consumable'] == 'Nitrogen']['rate'])],
    'Oxygen' : [int(threshold[threshold['threshold_category'] == 'Oxygen']['threshold_value']),int(rates[rates['affected_consumable'] == 'Oxygen']['rate'])],
    'Water' : [int(threshold[threshold['threshold_category'] == 'Water Alert']['threshold_value']),int(rates[rates['affected_consumable'] == 'Water']['rate'])]
    }

    if "ACY Insert" == type:
        actualRate = 
        actualthreshold = 
    elif "KTO" == type:
    elif "Pretreat Tanks" == type:
    elif "Filter Inserts" == type:
    elif "Urine Receptacle" == type:
    elif "EDVs" == type:
    elif 'Water'  == type:
    elif 'Oxygen' == type:
    elif 'Nitrogen' == type:
    return



def getThresholdLimit():
    data = pd.read_csv('/content/drive/Shareddrives/CS 4306 Barrios Project/csv Files/thresholds_limits_definition.csv') # needs to be changed
    data = data.copy(deep=True)

    # drops data with RSOS
    data.drop(data[data['threshold_owner'] == 'RSOS'].index, inplace = True)
    data = data[['threshold_category','threshold_value']]

    return data


def calculateCurrentRate():
    data = pd.read_csv('/content/drive/Shareddrives/CS 4306 Barrios Project/csv Files/rates_definition.csv') # needs to be changed
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
     

def numCrew():
    crew = pd.read_csv('/content/drive/Shareddrives/CS 4306 Barrios Project/csv Files/iss_flight_plan_crew_20220101-20251321.csv')
    crew = crew.copy(deep=True)

    # crew without russians :)
    nasa = crew[crew.nationality_category != 'RSA']
    nasa = nasa[crew.nationality_category != 'Commercial']
    nasa = nasa[crew.nationality_category != 'SFP']
    nasa = nasa[nasa.nationality_category != 'RSA, TBD']

    nasa = nasa.groupby('datedim', group_keys=False, as_index=False).sum()
    everyone = crew.groupby('datedim', group_keys=False, as_index=False).sum()

    return everyone, nasa


def combineRates():
    