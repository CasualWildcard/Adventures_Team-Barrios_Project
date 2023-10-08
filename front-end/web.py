import pandas as pd
import os
import gradio as gr
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes

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
#Manage Database catergory can be renamed
def testss(category):
    if "Tank Capacity" == category or "ISS Flight Plan Crew Nationality Lookup" == category or "ISS Flight Plan" == category:
        one=gr.Textbox(interactive=True, visible=True)
        two=gr.Textbox(interactive=True, visible=True)
        three=gr.Textbox(interactive=True, visible=True)
        four = gr.Textbox(interactive=True, visible=False)
        five = gr.Textbox(interactive=True, visible=False)
    elif "US Weekly Consumable Water Summary" == category:
        one=gr.Textbox(interactive=True, visible=True)
        two=gr.Textbox(interactive=True, visible=True)
        three=gr.Textbox(interactive=True, visible=True)
        four = gr.Textbox(interactive=True, visible=True)
        five = gr.Textbox(interactive=True, visible=True)
    elif "Thresholds/Limits" == category or "RS Weekly Consumable Water Summary" == category:
        one=gr.Textbox(interactive=True, visible=True)
        two=gr.Textbox(interactive=True, visible=True)
        three=gr.Textbox(interactive=True, visible=True)
        four = gr.Textbox(interactive=True, visible=True)
        five = gr.Textbox(interactive=True, visible=False)
    return(one,two,three,four,five)

#does authentication with the login cookies must be enabled in your browser to make this happen
def authentication(username,password):
    auth_usernames = "test"
    auth_passwords = "test"
    if username == auth_usernames and password == auth_passwords:
        return True
    return False

with gr.Blocks(theme=theme, title="Adventures") as mockup:
    with gr.Tab("Homepage"):
        homepage = gr.Label(value="Homepage")
        wiki = gr.Button(value="Link to Wiki", link="https://github.com/CasualWildcard/Adventures_Team-Barrios_Project")
    with gr.Tab("Imports"):
        homepage = gr.Label(value="Upload CSV Files")
        gr.Button(value="SUBMIT CSV'S", size = "lg")
        warningLabel = gr.Label(value = "Need to Submit all the CSV's Needed below!")
        with gr.Row():
            csv1 = gr.File(file_types = [".csv","txt"], label = "Tank Capacity", interactive = True)
            csv2 = gr.File(file_types = [".csv"], label = "US/RS Weekly Consumable Gas Summary", interactive = True)
            csv3 = gr.File(file_types = [".csv"], label = "US Weekly Consumable Water Summary", interactive = True)
            csv4 = gr.File(file_types = [".csv"], label = "RS Weekly Consumable Water Summary", interactive = True)
        with gr.Row():
            csv5 = gr.File(file_types = [".csv"], label = "IMS Consumables Category Lookup", interactive = True)
            csv6 = gr.File(file_types = [".csv"], label = "ISS Flight Plan Crew", interactive = True)
            csv7 = gr.File(file_types = [".csv"], label = "Rates Definition", interactive = True)
            csv8 = gr.File(file_types = [".csv"], label = "Thresholds/Limits", interactive = True)
        with gr.Row():
            csv9 = gr.File(file_types = [".csv"], label = "ISS Flight Plan Crew Nationality Lookup", interactive = True)
            csv10 = gr.File(file_types = [".csv"], label = "Inventory Management System Consumables", interactive = True)
            csv11 = gr.File(file_types = [".csv"], label = "ISS Flight Plan", interactive = True)
            csv12 = gr.File(file_types = [".csv"], label = "Stored Items Only Inventory Management System Consumables", interactive = True)
    with gr.Tab("Manage Database"):
        manage = gr.Label(value="Manage Database")
        mdCategoryDropdown = gr.Dropdown(choices = ["Tank Capacity", "US/RS Weekly Consumable Gas Summary", "US Weekly Consumable Water Summary",
                                                    "RS Weekly Consumable Water Summary", "IMS Consumables Category Lookup", "ISS Flight Plan Crew",
                                                      "Rates Definition", "Thresholds/Limits","ISS Flight Plan Crew Nationality Lookup", 
                                                      "Inventory Management System Consumables", "ISS Flight Plan", "Stored Items Only Inventory Management System Consumables"])
        with gr.Row():# more can be added 
            one = gr.Textbox(interactive=True, visible=False)
            two = gr.Textbox(interactive=True, visible=False)
            three = gr.Textbox(interactive=True, visible=False)
            four = gr.Textbox(interactive=True, visible=False)
            five = gr.Textbox(interactive=True, visible=False)
            mdCategoryDropdown.input(fn=testss, inputs=[mdCategoryDropdown], outputs=[one,two,three,four,five])
        with gr.Row():
            ones = gr.Textbox(interactive=True, visible=False)
            twos = gr.Textbox(interactive=True, visible=False)
            threes = gr.Textbox(interactive=True, visible=False)
            fours = gr.Textbox(interactive=True, visible=False)
            fives = gr.Textbox(interactive=True, visible=False)
            mdCategoryDropdown.input(fn=testss, inputs=[mdCategoryDropdown], outputs=[ones,twos,threes,fours,fives])
        with gr.Row():
            oness = gr.Textbox(interactive=True, visible=False)
            twoss = gr.Textbox(interactive=True, visible=False)
            threess = gr.Textbox(interactive=True, visible=False)
            fourss = gr.Textbox(interactive=True, visible=False)
            fivess = gr.Textbox(interactive=True, visible=False)
            mdCategoryDropdown.input(fn=testss, inputs=[mdCategoryDropdown], outputs=[oness,twoss,threess,fourss,fivess])
            

    with gr.Tab("View Analyses"):
        view = gr.Label(value="View Analyses")
        aCategoryDropdown = gr.Dropdown(interactive= True,choices = ["Historical Assumptions VS Actual Usage", 
                                                                     "Resupply Quantity Required", "Minimum Launch Vehicle Resupply Plan", "Minimun Supply Violation"])

mockup.launch(share=True, auth=authentication)#to turn off authentication just delete the auth part :)