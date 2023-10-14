import pandas as pd
from pandas import DataFrame
from pandasql import sqldf

# Sample Code: Please do not delete!
# query_results = sqldf('''SELECT * FROM test WHERE categoryID != 3''')
# test = pd.DataFrame(query_results)
# test.to_csv('back-end/test.csv')
"""
The sqldf() or read.csv.sql() functions can also be used to read filtered
files into R even if the original files are larger than R itself can handle
"""

def getRawFileUrl(url):
    return 'https://drive.google.com/uc?id=' + url.split('/')[-2]

test = pd.read_csv(getRawFileUrl('https://drive.google.com/file/d/12l2J2V5J5eHIvsJ6-DezH0s8olabrJGn/view?usp=sharing'))
#ims_consumables_category_lookup = pd.read_csv('https://drive.google.com/file/d/14s9Oi4CsvJTvQ63fajb2ODEceYU9GQel/view?usp=sharing')
#inventory_mgmt_system_consumables = pd.read_csv('https://drive.google.com/file/d/1BBZZn6asV4VDroOPKdxeSagUe-kDDm0b/view?usp=sharing')
#iss_flight_plan_2022_2025 = pd.read_csv('https://drive.google.com/file/d/18zafptSxQfgJoL0ARw6tmN5MK3z9BcmS/view?usp=sharing')
#iss_flight_plan_crew_2022_2025 = pd.read_csv('https://drive.google.com/file/d/1p03JnouYhLoebqSKeLxyiFhBVlEeUWBy/view?usp=sharing')
#iss_flight_plan_crew_nationality = pd.read_csv('https://drive.google.com/file/d/1i3sc7JbzZtDY9x1LREiCLbLOvYfizPRe/view?usp=sharing')
#rates_definition = pd.read_csv('https://drive.google.com/file/d/14DUA2SrvUN48q-XC2JQG8gss0MvGcSM7/view?usp=sharing')
#rsa_consumable_water_summary = pd.read_csv('https://drive.google.com/file/d/1hTwXM62DZdnoIPRdZ5uh8knM1Yu7He31/view?usp=sharing')
#stored_items_only_inventory_mgmt_system_consumables = pd.read_csv('https://drive.google.com/file/d/1ILcntB_qD6THeOnle7V7EVAmrIdHlDU3/view?usp=sharing')
#tank_capacity_definition = pd.read_csv('https://drive.google.com/file/d/1pxNGOsu0Qkv4PDSzgsyWFGGzWWJb32eo/view?usp=sharing')
#thresholds_limits_definition = pd.read_csv('https://drive.google.com/file/d/1QV3QCFL09TlH3B7SonSNdu04YBCSrAlQ/view?usp=sharing')
#us_rs_weekly_consumable_gas_summary = pd.read_csv('https://drive.google.com/file/d/1gDYYqm9SKBW1viN2uvtjOCUvc9-zul9F/view?usp=sharing')
#us_weekly_consumable_water_summary = pd.read_csv('https://drive.google.com/file/d/1vBrLR-DXDfDud1mHGwP9nwTiVbhR8gGP/view?usp=sharing')