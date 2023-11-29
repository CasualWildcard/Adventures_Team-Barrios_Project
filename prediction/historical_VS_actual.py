import datetime
from datetime import datetime

dateToday = datetime.now()
def getDropDates():

    data = pd.read_csv('/content/drive/Shareddrives/CS 4306 Barrios Project/csv Files/iss_flight_plan_20220101-20251231.csv') # change this to where the data is going to be imported
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


def compareRates(dropDates):

    # copys the dropDates and puts it into dates
    dates = dropDates.copy()

    # gets the consumables csv ofc need to change the read csv part :)
    consumables = pd.read_csv('/content/drive/Shareddrives/CS 4306 Barrios Project/csv Files/inventory_mgmt_system_consumables_20220101-20230905.csv')
    consumables = consumables.copy(deep=True)

    # since this data set does not have headers currently will place the headers with this :)
    consumables.columns =['datedim','id','id_parent','id_path','tree_depth','tree','part_number','serial_number','location_name','original_ip_owner','current_ip_owner','operational_nomenclature','russian_name','english_name','barcode','quantity','width','height','length','diameter','calculated_volume','stwg_ovrrd_vol','children_volume','stwg_ovrrd_chldren_vol','ovrrd_notes','volume_notes','expire_date','launch','type','hazard','state','status','is_container','is_moveable','system','subsystem','action_date','move_date','fill_status','categoryID','category_name']
    consumables["datedim"] = pd.to_datetime(consumables['datedim']) # turns the date dim column into datetime variable

    # turns the datedim into a YEAR-MONTH-DAY
    consumables['datedim'] = consumables['datedim'].astype(str)
    consumables['datedim'] = consumables['datedim'].apply(lambda x: x if len(x) < 11 else x[:10])
    consumables['datedim'] =  pd.to_datetime(consumables['datedim'])


    #note  does not focus on if us currently owns it
    #ITS ONLY WHICH CATEGORY THIS IS WE CAN MODIFY THIS BY GETTING ANOTHER COLUMN THEN SORTING IT BY THAT THEN DOING THIS 
    filterInsert = consumables.loc[consumables["category_name"] == 'Filter Inserts']
    filterInsert = filterInsert[['datedim', 'calculated_volume']]
    filterInsert = getActualUsageRates(filterInsert,dates)

    acyInserts = consumables.loc[consumables["category_name"] == 'ACY Inserts']
    acyInserts = acyInserts[['datedim', 'calculated_volume']]
    filterInsert = getActualUsageRates(filterInsert,dates)

    KTO = consumables.loc[consumables["category_name"] == 'KTO']
    KTO = KTO[['datedim', 'calculated_volume']]
    filterInsert = getActualUsageRates(filterInsert,dates)

    pretreat = consumables.loc[consumables["category_name"] == 'Pretreat Tanks']
    pretreat = pretreat[['datedim', 'calculated_volume']]
    filterInsert = getActualUsageRates(filterInsert,dates)

    foodRS = consumables.loc[consumables["category_name"] == 'Food-RS']
    foodRS = foodRS[['datedim', 'calculated_volume']]
    filterInsert = getActualUsageRates(filterInsert,dates)

    foodUS = consumables.loc[consumables["category_name"] == 'Food-US']  
    foodUS = foodUS[['datedim', 'calculated_volume']]
    filterInsert = getActualUsageRates(filterInsert,dates)

    urine = consumables.loc[consumables["category_name"] == 'EDV']
    urine = urine[['datedim', 'calculated_volume']]
    filterInsert = getActualUsageRates(filterInsert,dates)


def getActualUsageRates(dates,dataSet):

    #sums the calculated volume based on dates in the datedim column
    dataSet=dataSet.groupby("datedim", group_keys=False, as_index=False).sum()

    # does an intersetion between dates and dateset via the datedim column
    mergedData = pd.merge(dataSet, dates, how ='inner', on=['datedim'])

    #initializing a list
    result = []
    days =[]
    difference = []
    datesOfMission = []

    # initilalizing a final dataframe
    final = pd.DataFrame()

    # getting the lenght of the dataframe
    length = len(result.index)

    for index, row in mergedData.iterrows():
        if index + 1 != length:
            dividen = mergedData.at[index + 1, 'calculated_volume'] - mergedData.at[index, 'calculated_volume']
            divisor = mergedData.at[index + 1, 'datedim'] - mergedData.at[index, 'datedim']
            # appends dividen and divisor to days and difference so that we are able to create a dataframe
            difference.append(dividen)
            days.append(divisor)
            result.append(dividen/divisor.days)

            temp1 = mergedData.at[index + 2, 'datedim']
            temp1 = lasd.strftime("%B %d, %Y")

            temp2 = mergedData.at[index + 3, 'datedim']
            temp2 = lasdd.strftime("%B %d, %Y")

            datesOfMission.append(temp1 + ' - ' + temp2)

    final['Difference of Calculated Volumne'] = result
    final['days_between_missions'] = result
    final['rates'] = result        

    return final


