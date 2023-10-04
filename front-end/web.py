import gradio as gr
import pandas as pd
import os


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

with gr.Blocks(theme=theme) as mockup:
    with gr.Tab("Homepage"):
        homepage = gr.Label(value="Homepage")
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
"RS Weekly Consumable Water Summary", "IMS Consumables Category Lookup", "ISS Flight Plan Crew", "Rates Definition", "Thresholds/Limits",
"ISS Flight Plan Crew Nationality Lookup", "Inventory Management System Consumables", "ISS Flight Plan", "Stored Items Only Inventory Management System Consumables"])

    with gr.Tab("View Analyses"):
        view = gr.Label(value="View Analyses")
        aCategoryDropdown = gr.Dropdown(interactive= True,choices = ["Historical Assumptions VS Actual Usage", "Resupply Quantity Required", "Minimum Launch Vehicle Resupply Plan", "Minimun Supply Violation"])


mockup.launch(share=True)