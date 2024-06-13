import numpy as np
from matplotlib import pyplot as plt 
import os
import json

def extract_PID_data(data, PROTOCOL,LABEL):
    
    if(PROTOCOL == 'SAE_AVG'):

        if LABEL == 'IMFR': #Engine Inlet Air Mass Flow Rate 
            PID_TAG = 'spn_132_avg' 
        elif LABEL == 'EGR': #Exhaust Gas Recirculation (EGR) Mass Flow Rate
            PID_TAG = 'spn_2659_avg'
        elif LABEL == 'EGRDP': #Exhaust Gas Recirculation Differential Pressure
            PID_TAG = 'spn_412_avg'
        elif LABEL == 'EGRIP': #Engine Exhaust Gas Recirculation Inlet Pressure
            PID_TAG = 'spn_3358_avg'
        elif LABEL == 'EGRVC': #Engine Exhaust Gas Recirculation (EGR) Valve Control
            PID_TAG = 'spn_132_avg'
        elif LABEL == 'FRP':
            PID_TAG = 'spn_157_avg' 


    #print(LABEL)
    print("PID TAG is-->" + LABEL + " ," +PROTOCOL,"Mapping is --->", PID_TAG)

    Time_vec = []
    Val_vec = []
    #print(len(data[0]))
    #print(len(data))
    for data_cnt in range(0,len(data[0])):
        if "pids" in data[0][data_cnt]:
            if len(data[0][data_cnt]['pids'])>0:
                for sub_pid_cnt in range(0,len(data[0][data_cnt]['pids'])):  #this loop
                    State = data[0][data_cnt]['pids'][sub_pid_cnt]
                    #print(State)
                    #print(data_cnt)
                    #for state_cnt in range(0,len(State)):
                    if PID_TAG in State:
                        #print("--------------------------------------------IN----------------------------------")
                        Time_vec.append(np.array(State[PID_TAG]['timestamp'], dtype=np.int64))
                        Val_vec.append(np.array(State[PID_TAG]['value'], dtype=float))

    print("Number of time stamp avilables are--->",len(Val_vec))

    
    return Time_vec,Val_vec

if __name__ == '__main__':

    dir_list = ['1225921763074899968']
    PROTOCOL = 'SAE_AVG'

    for file in dir_list:
        print("Viechle ID-------", file)
        OBD_data_path = 'D:/Work/Timeseries_models/DATA/TH_DATA/EBT/T/' + file
        OBD_data = [json.loads(line) for line in open(OBD_data_path, 'r')]

        LABEL = 'FRP'
        X_Time, X_Value = extract_PID_data(OBD_data,PROTOCOL,LABEL)
        plt.subplot(4, 1, 1)
        plt.plot(X_Time,X_Value,'.b')
        plt.title(LABEL)

        LABEL = 'IMFR'
        X_Time, X_Value = extract_PID_data(OBD_data,PROTOCOL,LABEL)
        plt.subplot(4, 1, 2)
        plt.plot(X_Time,X_Value,'.b')
        plt.title(LABEL)

        LABEL = 'EGR'
        X_Time, X_Value = extract_PID_data(OBD_data,PROTOCOL,LABEL)
        plt.subplot(4, 1, 3)
        plt.plot(X_Time,X_Value,'.b')
        plt.title(LABEL)

        LABEL = 'EGRDP'
        X_Time, X_Value = extract_PID_data(OBD_data,PROTOCOL,LABEL)
        plt.subplot(4, 1, 4)
        plt.plot(X_Time,X_Value,'.b')
        plt.title(LABEL)

        plt.show()


