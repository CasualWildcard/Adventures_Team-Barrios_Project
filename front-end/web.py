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

def displayAnalysisDateRange(aCategoryDropdown):
    table = gr.DataFrame(visible = False)
    confirmDateButton = gr.Button(value="Confirm", show_label=False,visible=False)
    dataDropdown = gr.Dropdown(interactive=True, label="Which Threshold Violation", visible=False, choices= [])
    startDateCategoryDropdown = gr.Dropdown(interactive=True, visible=False, choices = availableDates)
    endDateCategoryDropdown = gr.Dropdown(interactive=True, visible=False, choices = availableDates)

    if aCategoryDropdown == "Historical Assumptions VS Actual Usage":
        dataDropdown = gr.Dropdown(interactive=True, label="Which Usage Rate", visible=True, choices= ["usageRateWater.csv",
                                                                                                            "usageRateNitrogen.csv",
                                                                                                            "usageRateOxygen.csv",
                                                                                                            "usageRateFilterInsert.csv",
                                                                                                            "usageRateKTO.csv",
                                                                                                            "usageRatePretreat.csv",
                                                                                                            "usageRateFoodUS.csv",
                                                                                                            "usageRateACY.csv"])
        confirmDateButton = gr.Button(value="Confirm", show_label=False,visible=True)

    elif aCategoryDropdown == "Resupply Quantity Required":
        dataDropdown = gr.Dropdown(interactive=True, label="Which Resupply Quantity", visible=True, choices= ["resultWater.csv",
                                                                                                            "resultNitrogen.csv",
                                                                                                            "resultOxygen.csv",
                                                                                                            "finalFilter.csv",
                                                                                                            "finalKTO.csv",
                                                                                                            "finalPretreat.csv",
                                                                                                            "finalFoodUS.csv",
                                                                                                            "finalACY.csv"])
        confirmDateButton = gr.Button(value="Confirm", show_label=False,visible=True)
    
    elif aCategoryDropdown == "Minimum Supply Violation":
        df = pd.read_csv("prediction/predictionsCSV/predictionQ4.csv")
        table = gr.DataFrame(value = df, visible = True)
    
    elif aCategoryDropdown == "Likely Threshold Violating Items":
        df = pd.read_csv("prediction/predictionsCSV/predictionTop5.csv")
        table = gr.DataFrame(value = df, visible = True)
    
    return dataDropdown, startDateCategoryDropdown, endDateCategoryDropdown, confirmDateButton, table, displayRate

def verifyDateRange(startDate, endDate):
    viewAnalysisError = gr.Label(value="", show_label=False)
    if startDate <= endDate:
        pass
    elif startDate > endDate:
        viewAnalysisError = gr.Label(value="Error: Start Date must be before End Date.", show_label=False)
    elif startDate == [] or endDate == []:
        viewAnalysisError = gr.Label(value="Error: One or both date values are empty.", show_label=False)
    return viewAnalysisError

def runAnalysisFun():
    os.system("python prediction/historical_VS_actual.py")

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
        whichResupplyQuantity = ""
        if dataDropdown == "resultWater.csv":
            whichResupplyQuantity = "water"
        elif dataDropdown == "resultNitrogen.csv":
            whichResupplyQuantity = "nitrogen"
        elif dataDropdown == "resultOxygen.csv":
            whichResupplyQuantity = "oxygen"
        elif dataDropdown == "finalFilter.csv":
            whichResupplyQuantity = "filter"
        elif dataDropdown == "finalKTO.csv":
            whichResupplyQuantity = "kto"
        elif dataDropdown == "finalPretreat.csv":
            whichResupplyQuantity = "pretreat"
        elif dataDropdown == "finalFoodUS.csv":
            whichResupplyQuantity = "food_us"
        elif dataDropdown == "finalACY.csv":
            whichResupplyQuantity = "acy"
        
        df = pd.read_csv("prediction/predictionsCSV/" + dataDropdown)
        df = df.iloc[:-1]

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df['datedim'], y=df['resupply_needed_' + whichResupplyQuantity], mode='lines', name='Resupply Quantity Required'))
        fig.add_trace(go.Scatter(x=df['datedim'], y=df['current_' + whichResupplyQuantity], mode='lines', name='Current In Storage'))

        fig.update_layout(title='Resupply Quantity Required vs Current In Storage', xaxis_title='Date', yaxis_title='Quantity')

        displayRate = gr.Plot(value=fig, visible = True)

    else:
        displayRate = gr.Plot(visible = False)

    if(endDate != 0):
        return displayRate, verifyDateRange(startDate, endDate)
    else:
        return displayRate, verifyDateRange(startDate, startDate)

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
            runAnalysis = gr.Button(value="Run Analysis", show_label=False,visible=True)
            runAnalysis.click(fn=runAnalysisFun, inputs=[], outputs=[])
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

    with gr.Tab("View Analyses"):
        view = gr.Label(value="View Analyses")
        aCategoryDropdown = gr.Dropdown(interactive= True,choices = ["Historical Assumptions VS Actual Usage", 
                                                                     "Resupply Quantity Required",
                                                                     "Minimum Supply Violation",
                                                                     "Likely Threshold Violating Items"])
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
            
        with gr.Row():    
            displayRate = gr.Plot(visible = False)
            displayTable = gr.DataFrame(visible = False)
        confirmButton = gr.Button(value="Confirm", show_label=False,visible=False)
        viewAnalysisError = gr.Label(value="", show_label=False)
        aCategoryDropdown.input(fn=displayAnalysisDateRange, inputs=[aCategoryDropdown], outputs=[dataDropdown, startDateCategoryDropdown,endDateCategoryDropdown, confirmButton, displayTable, displayRate])
        confirmButton.click(fn=loadAnalyses, inputs=[startDateCategoryDropdown, endDateCategoryDropdown, aCategoryDropdown, dataDropdown], outputs=[displayRate, viewAnalysisError])

mockup.launch(share=True)
