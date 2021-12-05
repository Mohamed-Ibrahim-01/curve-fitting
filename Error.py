import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

length_of_data=1000
loaded_ECG_data = pd.read_csv("emg.csv")
filtered_ECG_mV = loaded_ECG_data['filtered_ECG_mV']
time = loaded_ECG_data['time_sec']
def getError(function_degree,no_of_chuncks,overlapping):
    total_Residual = 0
    intervals = int(length_of_data/no_of_chuncks)
    for i in range(no_of_chuncks):
<<<<<<< HEAD
        if i == 0:
            coefficients, residual, _, _, _  = np.polyfit(time[i*intervals:intervals*(i+1)-1],filtered_ECG_mV[0+i*intervals:intervals*(i+1)-1],function_degree,full='true')
            total_Residual = total_Residual + residual
            # for illustration
            # print(i*intervals)
            # print(intervals*(i+1)-1)


        elif i<no_of_chuncks-1:
            coefficients, residual, _, _, _  = np.polyfit(time[i*intervals-int(i*intervals*(overlapping/100)):intervals*(i+1)-1-int(i*intervals*(overlapping/100))]
            ,filtered_ECG_mV[i*intervals-int(i*intervals*(overlapping/100)):intervals*(i+1)-1-int(i*intervals*(overlapping/100))],function_degree,full='true')
            total_Residual = total_Residual + residual
            # for illustration
            # print(i*intervals-int(i*intervals*(overlapping/100)))
            # print(intervals*(i+1)-1-int(i*intervals*(overlapping/100)))

        else:
            coefficients, residual, _, _, _  = np.polyfit(time[intervals*(i)-1-int((i-1)*intervals*(overlapping/100)):length_of_data]
            ,filtered_ECG_mV[intervals*(i)-1-int((i-1)*intervals*(overlapping/100)):length_of_data],function_degree,full='true')
            total_Residual = total_Residual + residual

            # for illustration
            # x = intervals*(i)-1-int((i-1)*intervals*(overlapping/100))
            # x = 1000-x
            # print(x)




    return total_Residual/np.sqrt(length_of_data)
=======
        coefficients, residual, _, _, _  = np.polyfit(time[i*intervals:intervals*(i+1)-1],filtered_ECG_mV[0+i*intervals:intervals*(i+1)-1],function_degree,full='true')
        total_Residual = total_Residual + residual
    return total_Residual/length_of_data
>>>>>>> e2fda81f91a67a4dd78a8c35582b84c5ade5de93
        
    




# print(getError(4,6,90))
# print(getError(4,6,0))







