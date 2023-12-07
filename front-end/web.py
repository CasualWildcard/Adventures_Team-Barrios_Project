import os
import pandas as pd
import gradio as gr
import matplotlib.pyplot as plt
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes
import mplcursors
import plotly.graph_objects as go

CSVHeaders = {
    'tankCapacity' : ["tank_category", "tank_capacity", "units"],
    'issFlightPlan' : ["datedim", "vehicle_name", "port_name", "vehicle_type", "eva_name", "eva_type", "eva_accuracy", "event"],
    'crewNationalityLookup' : ["nationality", "is_usos_crew", "is_rsa_crew"],
    'ratesDefinition' : ["rate_category", "affected_consumable", "rate", "units", "type", "efficiency"],
    'usWeeklyWaterSummary' : ["Date", "Corrected Potable (L)", "Corrected Technical  (L)", "Corrected Total (L)", "Resupply Potable (L)", "Resupply Technical (L)", "Corrected Predicted (L)", 'Unnamed: 7', 'Unnamed: 8'],
    'IMSConsumables' : ["category_name", "categoryID", "module_name", "moduleID", "unique_cat_mod_ID"],
    'issFlightPlanCrew' : ["datedim", "nationality_category", "crew_count"],
    'thresholdLimits' : ["threshold_category", "threshold_value", "threshold_owner", "units"],
    'rsaWeeklyWaterSummary' : ["Report Date", "Remain. Potable (liters)", "Remain. Technical (liters)", "Remain. Rodnik (liters)"],
    'weeklyGasSummary' : ["Date", "USOS O2 (kg)", "RS O2 (kg)", "US N2 (kg)", "RS N2 (kg)", "Adjusted O2 (kg)", "Adjusted N2 (kg)", "Resupply O2 (kg)", "Resupply N2 (kg)", "Resupply Air (kg)"],
    'storedItemsOnlyIMS' : ["datedim", "id", "id_parent", "id_path", "tree_depth", "tree", "part_number", "serial_number", "location_name", "original_ip_owner", "current_ip_owner", "operational_nomenclature", "russian_name", "english_name", "barcode", "quantity", "width", "height", "length", "diameter", "calculated_volume", "stwg_ovrrd_vol", "children_volume", "stwg_ovrrd_chldrn_vol", "ovrrd_notes", "volume_notes", "expire_date", "launch", "type", "hazard", "state", "status", "is_container", "is_moveable", "system", "subsystem", "action_date", "move_date", "fill_status", "categoryID", "category_name"]
}

availableDates = ["2023-08-01", "2023-09-01", "2023-10-01"]

theme = gr.themes.Base(
    font=[gr.themes.GoogleFont('Montserrat'), 'ui-sans-serif', 'system-ui', 'sans-serif'],
    font_mono=[gr.themes.GoogleFont('sans-serif'), 'ui-monospace', 'Consolas', 'monospace'],
).set(
    body_background_fill='#f7f7f7',
    body_text_color='black',
    body_text_color_subdued='#4b5563',
    background_fill_primary='#ededed',
    background_fill_secondary='white',
    border_color_accent_subdued='#4b5563',
    border_color_primary='black',
    color_accent='#93c5fd',
    chatbot_code_background_color='#1f2937',
    chatbot_code_background_color_dark='1e40af',
    checkbox_background_color_dark='85beff',
    button_large_text_size='text_xl',
    button_large_text_weight='800',
    button_primary_background_fill='#93c5fd',
    button_primary_background_fill_hover='#86bcf',
    button_primary_border_color='black',
    button_primary_text_color='black',
    button_primary_text_color_hover='#60a5fa',
    button_secondary_background_fill='#dbeafe'
)
def test(a):
    return

#Manage Database catergory can be renamed
def updateColumns(category):
    buttonChange = gr.Button(visible=True)
    if "Tank Capacity" == category:
        firstColumn=gr.Textbox(interactive=True, visible=True, label="Tank Category")
        secondColumn=gr.Textbox(interactive=True, visible=True, label="Tank Capacity")
        thirdColumn=gr.Textbox(interactive=True, visible=True, label="Units")
        fourthColumn = gr.Textbox(interactive=True, visible=False)
        fifthColumn = gr.Textbox(interactive=True, visible=False)
        sixthColumn = gr.Textbox(interactive=True, visible=False)
        seventhColumn = gr.Textbox(interactive=True, visible=False)
    elif "ISS Flight Plan" == category:
        firstColumn=gr.Textbox(interactive=True, visible=True, label="Event Name")
        secondColumn=gr.Textbox(interactive=True, visible=True, label="Port Name")
        thirdColumn=gr.Textbox(interactive=True, visible=True, label="Vehicle Type")
        fourthColumn = gr.Textbox(interactive=True, visible=True, label="Date")
        fifthColumn = gr.Textbox(interactive=True, visible=True, label="Eva Type")
        sixthColumn = gr.Textbox(interactive=True, visible=True, label="Eva Accuracy")
        seventhColumn = gr.Textbox(interactive=True, visible=True, label="Event")
    elif "ISS Flight Plan Crew Nationality Lookup" == category:
        firstColumn=gr.Textbox(interactive=True, visible=True, label="Nationality")
        secondColumn=gr.Textbox(interactive=True, visible=True, label="USOS Crew")
        thirdColumn=gr.Textbox(interactive=True, visible=True, label="RSA Crew")
        fourthColumn = gr.Textbox(interactive=True, visible=False)
        fifthColumn = gr.Textbox(interactive=True, visible=False)
        sixthColumn = gr.Textbox(interactive=True, visible=False)
        seventhColumn = gr.Textbox(interactive=True, visible=False)
    elif "Rates Definition" == category:
        firstColumn=gr.Textbox(interactive=True, visible=True, label="Rate Category")
        secondColumn=gr.Textbox(interactive=True, visible=True, label="Type")
        thirdColumn=gr.Textbox(interactive=True, visible=True, label="Affected Consumable")
        fourthColumn = gr.Textbox(interactive=True, visible=True, label="Rate")
        fifthColumn = gr.Textbox(interactive=True, visible=True, label="Units")
        sixthColumn = gr.Textbox(interactive=True, visible=True, label="Efficiency")
        seventhColumn = gr.Textbox(interactive=True, visible=False)
    elif "US Weekly Consumable Water Summary" == category:
        firstColumn=gr.Textbox(interactive=True, visible=True, label="Date")
        secondColumn=gr.Textbox(interactive=True, visible=True, label="Corrected Potable")
        thirdColumn=gr.Textbox(interactive=True, visible=True, label="Corrected Technical")
        fourthColumn = gr.Textbox(interactive=True, visible=True, label="Corrected Total")
        fifthColumn = gr.Textbox(interactive=True, visible=True, label="Resupply Potable")
        sixthColumn = gr.Textbox(interactive=True, visible=True, label="Resupply Technical")
        seventhColumn = gr.Textbox(interactive=True, visible=True, label="Corrected Predicted")
    elif "IMS Consumables" == category:
        firstColumn=gr.Textbox(interactive=True, visible=True, label="Category Name")
        secondColumn=gr.Textbox(interactive=True, visible=True, label="Category ID")
        thirdColumn=gr.Textbox(interactive=True, visible=True, label="Module Name")
        fourthColumn = gr.Textbox(interactive=True, visible=True, label="Module ID")
        fifthColumn = gr.Textbox(interactive=True, visible=True, label="Unique Cat Mod ID")
        sixthColumn = gr.Textbox(interactive=True, visible=False)
        seventhColumn = gr.Textbox(interactive=True, visible=False)
    elif "Thresholds/Limits" == category:
        firstColumn=gr.Textbox(interactive=True, visible=True, label="Threshold Category")
        secondColumn=gr.Textbox(interactive=True, visible=True, label="Threshold Value")
        thirdColumn=gr.Textbox(interactive=True, visible=True, label="Threshold Owner")
        fourthColumn = gr.Textbox(interactive=True, visible=True, label="Units")
        fifthColumn = gr.Textbox(interactive=True, visible=False)
        sixthColumn = gr.Textbox(interactive=True, visible=False)
        seventhColumn = gr.Textbox(interactive=True, visible=False)
    elif "RS Weekly Consumable Water Summary" == category:
        firstColumn=gr.Textbox(interactive=True, visible=True, label="Report Date")
        secondColumn=gr.Textbox(interactive=True, visible=True, label="Remain. Potable(Liters)")
        thirdColumn=gr.Textbox(interactive=True, visible=True, label="Rmain Technical(Liters)")
        fourthColumn = gr.Textbox(interactive=True, visible=True, label="Remain Rodnik(Liters)")
        fifthColumn = gr.Textbox(interactive=True, visible=False)
        sixthColumn = gr.Textbox(interactive=True, visible=False)
        seventhColumn = gr.Textbox(interactive=True, visible=False)
    return(buttonChange,firstColumn,secondColumn,thirdColumn,fourthColumn,fifthColumn,sixthColumn,seventhColumn)

def displayAnalysisDateRange(aCategoryDropdown):
    if aCategoryDropdown == "Historical Assumptions VS Actual Usage":
        dataDropdown = gr.Dropdown(interactive=True, label="Which Usage Rate", visible=True, choices= ["usageRateWater.csv",
                                                                                                            "usageRateNitrogen.csv",
                                                                                                            "usageRateOxygen.csv",
                                                                                                            "usageRateFilterInsert.csv",
                                                                                                            "usageRateKTO.csv",
                                                                                                            "usageRatePretreat.csv",
                                                                                                            "usageRateFoodUS.csv"])
        startDateCategoryDropdown = gr.Dropdown(interactive=True, visible=True, choices = availableDates)
        endDateCategoryDropdown = gr.Dropdown(interactive=True, visible=True, choices = availableDates)

    elif aCategoryDropdown == "Resupply Quantity Required":
        dataDropdown = gr.Dropdown(interactive=True, label="Which Resupply Quantity", visible=True, choices= ["resupplyQuantityWater.csv",
                                                                                                            "resupplyQuantityNitrogen.csv",
                                                                                                            "resupplyQuantityOxygen.csv",
                                                                                                            "resupplyQuantityFilterInsert.csv",
                                                                                                            "resupplyQuantityKTO.csv",
                                                                                                            "resupplyQuantityPretreat.csv",
                                                                                                            "resupplyQuantityFoodUS.csv"])
        startDateCategoryDropdown = gr.Dropdown(interactive=True, visible=True, choices = availableDates)
        endDateCategoryDropdown = gr.Dropdown(interactive=True, visible=False, choices = availableDates)
    
    else:
        startDateCategoryDropdown = gr.Dropdown(interactive=True, visible=True, choices = availableDates)
        endDateCategoryDropdown = gr.Dropdown(interactive=True, visible=True, choices = availableDates)
    confirmDateButton = gr.Button(value="Confirm", show_label=False,visible=True)
    return dataDropdown, startDateCategoryDropdown, endDateCategoryDropdown, confirmDateButton

def verifyDateRange(startDate, endDate):
    viewAnalysisError = gr.Label(value="", show_label=False)
    if startDate <= endDate:
        pass
    elif startDate > endDate:
        viewAnalysisError = gr.Label(value="Error: Start Date must be before End Date.", show_label=False)
    elif startDate == [] or endDate == []:
        viewAnalysisError = gr.Label(value="Error: One or both date values are empty.", show_label=False)
    return viewAnalysisError

def loadAnalyses(startDate, endDate, aCategoryDropdown, dataDropdown):
    
    if aCategoryDropdown == "Historical Assumptions VS Actual Usage":
        # Load the data
        df = pd.read_csv("prediction/predictionsCSV/" + dataDropdown)

        # Create a plot
        fig = go.Figure()

        if (dataDropdown == "usageRateACY.csv" or dataDropdown == "usageRateFoodUS.csv" or dataDropdown == "usageRateKTO.csv" or dataDropdown == "usageRatePretreat.csv" or dataDropdown == "usageRateFilterInsert.csv"):
            # Add traces
            fig.add_trace(go.Scatter(x=df['days_since_resupply'], y=df['actual_loss'], mode='lines', name='Actual Loss'))
            fig.add_trace(go.Scatter(x=df['days_since_resupply'], y=df['assumed_loss'], mode='lines', name='Assumed Loss'))

            # Set layout properties
            fig.update_layout(title='Actual Loss vs Assumed Loss', xaxis_title='Days Since Resupply', yaxis_title='Loss')
        else:
            # Add traces
            fig.add_trace(go.Scatter(x=df['days_since_resupply'], y=df['actual_rate_per/day'], mode='lines', name='Actual Usage Rate'))
            fig.add_trace(go.Scatter(x=df['days_since_resupply'], y=df['rate_per_day'], mode='lines', name='Assumed Usage Rate'))

            # Set layout properties
            fig.update_layout(title='Actual Usage Rate vs Assumed Usage Rate', xaxis_title='Days Since Resupply', yaxis_title='Usage Rate')
        displayRate = gr.Plot(value=fig, visible = True)
    
    elif aCategoryDropdown == "Resupply Quantity Required":
        displayRate = gr.DataFrame(value=pd.read_csv("prediction/predictionsCSV/" + dataDropdown), visible = True)
        
    #elif aCategoryDropdown == "Minimum Launch Vehicle Resupply Plan":

    #elif aCategoryDropdown == "Minimun Supply Violation":
    
    if(endDate != 0):
        return displayRate, verifyDateRange(startDate, endDate)
    else:
        return displayRate, verifyDateRange(startDate, startDate)

#does authentication with the login cookies must be enabled in your browser to make this happen
def authentication(username,password):
    auth_usernames = "test"
    auth_passwords = "test"
    if username == auth_usernames and password == auth_passwords:
        return True
    return False

def openFile(fileName):
    viewDownloadError = gr.Label(value="", show_label=False)
    try:
        os.system("start EXCEL.EXE " + "back-end/csvStorage/" + fileName + ".csv")
        viewDownloadError = gr.Label(value="File now opening", show_label=False)
    except:
        viewDownloadError = gr.Label(value="Error: File does not exist. No such file has been submitted yet.", show_label=False)
    return viewDownloadError

def importCSV(csvdata):
    outputTypes = [] # Debug list to ensure that the file is being read correctly
    name = 'back-end/csvStorage/' # File name, taken from key in for loop below
    
    for csv in csvdata: # Iterate through all uploaded CSV files
      try: # If the CSV is entirely blank, Pandas will throw an error. This catches it.
        data = pd.read_csv(csv.name) # Imports CSV into a dataframe 'data'
        if data.empty: # Makes sure there's data in the dataframe
            outputTypes += ["Error: CSV file is empty or has no data."] # Can be replaced with proper error display later, does not account for null entries.
        isValid = False
        for key, value in CSVHeaders.items(): #Iterate through all valid data headers
            if value == list(data.columns.values): #If CSV headers match a valid data header
                # Replace next line with a function to pass the valid dataframe to the backend
                outputTypes += [key]
                isValid = True
                name += key
                break
        if not isValid:        
          outputTypes += ["Error: CSV does not match known data file types."] # Can be replaced with proper error display later
        else:
          name += '.csv'
          data.to_csv(name)
      except pd.errors.EmptyDataError:
          outputTypes += ["Error: CSV file is either completely blank or has no data."] # Can be replaced with proper error display later
    return outputTypes

with gr.Blocks(theme=theme, title="Adventures") as mockup:
    with gr.Tab("Homepage"):
        homepage = gr.Label(value="Homepage")
        wiki = gr.Button(value="Link to Wiki", link="https://github.com/CasualWildcard/Adventures_Team-Barrios_Project/wiki")
    with gr.Tab("Imports"):
        homepage = gr.Label(value="Upload CSV Files")
        # warningLabel = gr.Label(value = "Need to Submit all the CSV's Needed below!", scale=5)
        with gr.Row():
            csv1 = gr.Interface(importCSV, gr.File(file_types = [".csv"], file_count = "multiple", label = "Insert Any Data File Here"), "text", allow_flagging='never')
        with gr.Row():
            downloadDropdown = gr.Dropdown(interactive=True, choices = ['tankCapacity',
                                                      'issFlightPlan',
                                                      'crewNationalityLookup',
                                                      'ratesDefinition',
                                                      'usWeeklyWaterSummary',
                                                      'IMSConsumables',
                                                      'issFlightPlanCrew',
                                                      'thresholdLimits',
                                                      'rsaWeeklyWaterSummary',
                                                      'weeklyGasSummary',
                                                      'storedItemsOnlyIMS'])
        with gr.Row():
            viewDownloadError = gr.Label(value="", show_label=False)
            downloadButton = gr.Button(value="Edit in Excel", show_label=False, visible=True)
            downloadButton.click(fn=openFile, inputs=[downloadDropdown], outputs=[viewDownloadError])

    with gr.Tab("Manage Database"):
        manage = gr.Label(value="Manage Database")
        mdCategoryDropdown = gr.Dropdown(choices = ["Tank Capacity", "US/RS Weekly Consumable Gas Summary", 
                                                    "US Weekly Consumable Water Summary",
                                                    "RS Weekly Consumable Water Summary", 
                                                    "IMS Consumables", "ISS Flight Plan Crew",
                                                    "Rates Definition", "Thresholds/Limits",
                                                    "ISS Flight Plan Crew Nationality Lookup", 
                                                    "Inventory Management System Consumables",
                                                    "ISS Flight Plan", 
                                                    "Stored Items Only Inventory Management System Consumables"])
        with gr.Row():# more can be added
            addButton = gr.Button(value="Add", show_label=False,visible=False)
            addFirstColumn = gr.Textbox(interactive=True, visible=False)
            addSecondColumn = gr.Textbox(interactive=True, visible=False)
            addThirdColumn = gr.Textbox(interactive=True, visible=False)
            addFourthColumn = gr.Textbox(interactive=True, visible=False)
            addFifthColumn = gr.Textbox(interactive=True, visible=False)
            addSixthColumn = gr.Textbox(interactive=True, visible=False)
            addSeventhColumn = gr.Textbox(interactive=True, visible=False)
            # gr.Interface(fn=test, inputs=[addFirstColumn,addSecondColumn,addThirdColumn,addFourthColumn,addFifthColumn,addSixthColumn,addSeventhColumn], outputs=asd, allow_flagging="never",title="Add Data to Database")
            mdCategoryDropdown.input(fn=updateColumns, inputs=[mdCategoryDropdown],
                                    outputs=[addButton,addFirstColumn,addSecondColumn,addThirdColumn,
                                            addFourthColumn,addFifthColumn,addSixthColumn,
                                             addSeventhColumn])
        with gr.Row():
            removeButton = gr.Button(value="Remove", show_label=False,visible=False)
            removeFirstColumn = gr.Textbox(interactive=True, visible=False)
            removeSecondColumn = gr.Textbox(interactive=True, visible=False)
            removeThirdColumn = gr.Textbox(interactive=True, visible=False)
            removeFourthColumn = gr.Textbox(interactive=True, visible=False)
            removeFifthColumn = gr.Textbox(interactive=True, visible=False)
            removeSixthColumn = gr.Textbox(interactive=True, visible=False)
            removeSeventhColumn = gr.Textbox(interactive=True, visible=False)
            mdCategoryDropdown.input(fn=updateColumns, inputs=[mdCategoryDropdown],
                                      outputs=[removeButton,removeFirstColumn,removeSecondColumn,removeThirdColumn
                                               ,removeFourthColumn,removeFifthColumn,removeSixthColumn
                                               ,removeSeventhColumn])
        with gr.Row():
            modifyButton = gr.Button(value="Modify", show_label=False,visible=False)
            modifyFirstColumn = gr.Textbox(interactive=True, visible=False)
            modifySecondColumn = gr.Textbox(interactive=True, visible=False)
            modifyThirdColumn = gr.Textbox(interactive=True, visible=False)
            modifyFourthColumn = gr.Textbox(interactive=True, visible=False)
            modifyFifthColumn = gr.Textbox(interactive=True, visible=False)
            modifySixthColumn = gr.Textbox(interactive=True, visible=False)
            modifySeventhColumn = gr.Textbox(interactive=True, visible=False)
            mdCategoryDropdown.input(fn=updateColumns, inputs=[mdCategoryDropdown],
                                      outputs=[modifyButton,modifyFirstColumn,modifySecondColumn,modifyThirdColumn,
                                               modifyFourthColumn,modifyFifthColumn,modifySixthColumn,
                                               modifySeventhColumn])
    with gr.Tab("View Analyses"):
        view = gr.Label(value="View Analyses")
        aCategoryDropdown = gr.Dropdown(interactive= True,choices = ["Historical Assumptions VS Actual Usage", 
                                                                     "Resupply Quantity Required",
                                                                       "Minimum Launch Vehicle Resupply Plan",
                                                                         "Minimun Supply Violation"])
        with gr.Row():
            startDateCategoryDropdown = gr.Dropdown(interactive=True, label="Start Date", visible=False, choices = availableDates)
            endDateCategoryDropdown = gr.Dropdown(interactive=True, label="End Date", visible=False, choices = availableDates)
            dataDropdown = gr.Dropdown(interactive=True, label="Which Usage Rate", visible=False, choices= ["usageRateWater.csv",
                                                                                      "usageRateNitrogen.csv",
                                                                                      "usageRateOxygen.csv",
                                                                                      "usageRateFilterInsert.csv",
                                                                                      "usageRateKTO.csv",
                                                                                      "usageRatePretreat.csv",
                                                                                      "usageRateFoodUS.csv",
                                                                                      "usageRateACY.csv"])
            #dataDropdown = gr.Dropdown(interactive=True, label="Which Resupply Quantity", visible=False, choices= ["resupplyQuantityWater.csv",
            #                                                                          "resupplyQuantityNitrogen.csv",
            #                                                                          "resupplyQuantityOxygen.csv",
            #                                                                          "resupplyQuantityFilterInsert.csv",
            #                                                                          "resupplyQuantityKTO.csv",
            #                                                                          "resupplyQuantityPretreat.csv",
            #                                                                          "resupplyQuantityFoodUS.csv"])
        with gr.Row():    
            displayRate = gr.Plot(visible = False)
        confirmButton = gr.Button(value="Confirm", show_label=False,visible=False)
        viewAnalysisError = gr.Label(value="", show_label=False)
        aCategoryDropdown.input(fn=displayAnalysisDateRange, inputs=[aCategoryDropdown], outputs=[dataDropdown, startDateCategoryDropdown,endDateCategoryDropdown, confirmButton])
        confirmButton.click(fn=loadAnalyses, inputs=[startDateCategoryDropdown, endDateCategoryDropdown, aCategoryDropdown, dataDropdown], outputs=[displayRate, viewAnalysisError])

mockup.launch(share=True)#to turn off authentication just delete the auth part :)
