import numpy as np
from matplotlib import pyplot as plt 
import os
from scipy import signal


def extract_PID_data(data, PROTOCOL,LABEL,PLOT_FLAG):

    if(PROTOCOL == 'SAE_AVG'):

        if LABEL == 'ENGINE LOAD':
            PID_TAG = 'spn_92_avg'
        elif LABEL == 'ENGINE RPM':
            PID_TAG = 'spn_190_avg'
        elif LABEL == 'THROTTLE':
            PID_TAG = 'spn_91_avg'
        elif LABEL == 'SPEED': # Wheep based Vehicle Speed
            PID_TAG = 'spn_84_avg'
        elif LABEL == 'FRP':
            PID_TAG = 'spn_157_avg' # 245 

    print("PID TAG is-->" + LABEL + " ," +PROTOCOL,"Mapping is --->", PID_TAG)

    Time_vec = []
    Val_vec = []
    #print(len(data[0]))
    #data = data[0]
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

    if (PLOT_FLAG == 1):            
        plt.title("Time Series") 
        plt.xlabel("Time Stamp") 
        plt.ylabel(LABEL) 
        plt.scatter(Time_vec,Val_vec) 
        plt.show()
                
    return Time_vec,Val_vec

def resample_PID_data(X_Value,Number_of_features):

    # DPFDP has minimum length DATA[1,:], so resample all other variables  w.r.t. DPFDP
    Samples = len(X_Value[0])
    #print(len(X_Value[0]))
    DATA = np.zeros((Number_of_features,Samples))
    TEMP = np.transpose(np.array(X_Value[0]))
 
    for cnt in range(0,Number_of_features):
        if (len(X_Value[cnt]) > 0):
            DATA[cnt,:] = np.transpose(np.array(signal.resample(X_Value[cnt], Samples)))

    DATA[0,:] = TEMP

    return DATA

def RPM_Contraint(DATA,T1,RANGE):

    TEMP = DATA[1,:] # 1st is RPM
    nums = TEMP[(RANGE[0] < TEMP) & (TEMP <= RANGE[1])]
    Samples = len(nums)
    #print(Samples)
    DATA_OUT = np.zeros((DATA.shape[0],Samples))
    T_OUT = np.zeros(Samples)

    out_cnt = 0

    for cnt in range(0,DATA.shape[1]):
        if ((RANGE[0] < TEMP[cnt]) and (TEMP[cnt] <= RANGE[1])):
            for var_cnt in range(0,DATA.shape[0]):
                DATA_OUT[var_cnt,out_cnt] = DATA[var_cnt,cnt]
            T_OUT[out_cnt] = T1[cnt]
            out_cnt = out_cnt + 1

    return DATA_OUT,T_OUT
    

def Throttle_Contraint(DATA,T2,TH):

    TEMP = DATA[2,:] # 7th is Throttle
    nums = TEMP[(TH < TEMP)]
    Samples = len(nums)
    #print(Samples)
    DATA_OUT = np.zeros((DATA.shape[0],Samples))
    T_OUT = np.zeros(Samples)

    out_cnt = 0

    for cnt in range(0,DATA.shape[1]):
        if (TH < TEMP[cnt]):
            for var_cnt in range(0,DATA.shape[0]):
                DATA_OUT[var_cnt,out_cnt] = DATA[var_cnt,cnt]
            T_OUT[out_cnt] = T2[cnt]
            out_cnt = out_cnt + 1

    return DATA_OUT,T_OUT

def Engine_load_Contraint(DATA,T3,TH):

    TEMP = DATA[3,:] # 3rd is load
    nums = TEMP[(TH < TEMP)]
    Samples = len(nums)
    #print(Samples)
    DATA_OUT = np.zeros((DATA.shape[0],Samples))
    T_OUT = np.zeros(Samples)

    out_cnt = 0

    for cnt in range(0,DATA.shape[1]):
        if (TH < TEMP[cnt]):
            for var_cnt in range(0,DATA.shape[0]):
                DATA_OUT[var_cnt,out_cnt] = DATA[var_cnt,cnt]
            T_OUT[out_cnt] = T3[cnt]
            out_cnt = out_cnt + 1

    return DATA_OUT,T_OUT

def idle_Contraint(DATA,T4,TH):

    TEMP = DATA[4,:] 
    nums = TEMP[(TH < TEMP)]
    Samples = len(nums)
    #print(Samples)
    DATA_OUT = np.zeros((DATA.shape[0],Samples))
    T_OUT = np.zeros(Samples)

    out_cnt = 0

    for cnt in range(0,DATA.shape[1]):
        if (TH < TEMP[cnt]):
            for var_cnt in range(0,DATA.shape[0]):
                DATA_OUT[var_cnt,out_cnt] = DATA[var_cnt,cnt]
            T_OUT[out_cnt] = T4[cnt]
            out_cnt = out_cnt + 1

    return DATA_OUT,T_OUT



