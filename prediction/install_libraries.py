import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from prophet import Prophet
from auto_ts import auto_timeseries

import subprocess, sys
import os

file = "install_libaries.ps1"
dir_path = os.path.dirname(os.path.realpath(file))
x = dir_path.split('\\')
dir_path = "\\\\".join(x)
print(dir_path)
dir_path = dir_path +'\\' + file
p = subprocess.Popen(["powershell.exe", 
              dir_path], 
              stdout=sys.stdout)
p.communicate()


    