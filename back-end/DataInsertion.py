import pandas as pd
import numpy as np
from dask import dataframe as dd
df = pd.read_csv('https://raw.githubusercontent.com/facebook/prophet/main/examples/example_wp_log_peyton_manning.csv')
print("Running FB Prophet test:")
df.head()