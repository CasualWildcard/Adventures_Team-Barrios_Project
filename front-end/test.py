import gradio as gr
import pandas as pd
import os

ims_consumables_category_lookup = pd.read_csv(r"C:\Users\cblick\Desktop\Project Barrios\Adventures_Team-Barrios_Project\back-end\csvStorage\rsa_consumable_water_summary_20220103-20230828.csv")

with gr.Blocks() as mockup:
    with gr.Tab("Homepage"):
      gr.Dataframe(ims_consumables_category_lookup)

mockup.launch(share=True)