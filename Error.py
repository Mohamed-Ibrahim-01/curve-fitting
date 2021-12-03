import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

length_of_data=401
loaded_ECG_data = pd.read_csv("emg.csv")
filtered_ECG_mV = loaded_ECG_data['filtered_ECG_mV']
time = loaded_ECG_data['time_sec']
def getError(function_degree,no_of_chuncks):
    total_Residual = 0
    

    intervals = int(length_of_data/no_of_chuncks)
    for i in range(no_of_chuncks):
        coefficients, residual, _, _, _  = np.polyfit(time[i*intervals:intervals*(i+1)-1],filtered_ECG_mV[0+i*intervals:intervals*(i+1)-1],function_degree,full='true')
        print(residual)
        total_Residual = total_Residual + residual
    return total_Residual/length_of_data
        
    
print(getError(4,4))











