import numpy as np
from matplotlib import pyplot as plt 
import os
import json

def extract_PID_data(data, PROTOCOL,LABEL):

    if(PROTOCOL == 'SAE'):

        if LABEL == 'ENGINE LOAD':
            PID_TAG = '92'
        elif LABEL == 'ENGINE RPM':
            PID_TAG = '190'
        elif LABEL == 'THROTTLE':
            PID_TAG = '91'
        elif LABEL == 'FUEL RATE':
            PID_TAG = '183'
        elif LABEL == 'SPEED': # Wheep based Vehicle Speed
            PID_TAG = '84'
        elif LABEL == 'FRP':
            PID_TAG = '157' # 245 

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

    dir_list = ['1231762781519216640']
    PROTOCOL = 'SAE_AVG'

    for file in dir_list:
        print("Viechle ID-------", file)
        #OBD_data_path = 'D:/Work/FRP/DATA/WITH_157/' + file
        OBD_data_path = 'D:/Work/FRP/DATA/FOTA/EBT/Kenworth - Cummins X15/' + file
        #OBD_data_path = 'D:/Work/Timeseries_models/DATA/TH_DATA/EBT/T/' + file
        OBD_data = [json.loads(line) for line in open(OBD_data_path, 'r')]

        LABEL = 'FRP'
        X_Time_frp , X_Value_frp = extract_PID_data(OBD_data,PROTOCOL,LABEL)
        print(np.array(X_Time_frp[0]))
        print(np.array(X_Time_frp[-1]))

        fig, ax1 = plt.subplots()
        ax1.plot(X_Time_frp,X_Value_frp,'g.')
        ax1.set_xlabel('Time') 
        ax1.set_ylabel('Fuel Rail Pressure in MPa')
        ax1.grid()

        LABEL = 'ENGINE RPM'
        X_Time_rpm, X_Value_rmp = extract_PID_data(OBD_data,PROTOCOL,LABEL)
        print(np.array(X_Time_rpm[0]))
        print(np.array(X_Time_rpm[-1]))

        #fig, ax2 = plt.subplots()
        #ax2.plot(X_Time_rpm,X_Value_rmp,'g.')
        #plt.show()
        #exit(0)

        '''
        col=[]
        for i in range(0,len(X_Value_frp)):
            if X_Value_rmp[i]<800:
                col.append('RPM<800')
            elif X_Value_rmp[i]>=800 and X_Value_rmp[i]<=1200:
                col.append('800<PRM<1200')
            elif X_Value_rmp[i]>=1200 and X_Value_rmp[i]<=1600:
                col.append('1200<PRM<1600')
            elif X_Value_rmp[i]>=1600 and X_Value_rmp[i]<=1800:
                col.append('1600<PRM<1800')
            else:
                col.append('RPM>1800')

        #scatter plot
        CC = ['g','y','c','m','r']
        cnt = 0
        for color in set(col):
            x_values = [X_Time_frp[i] for i in range(len(X_Time_frp)) if col[i] == color]
            y_values = [X_Value_frp[i] for i in range(len(X_Value_frp)) if col[i] == color]
            COL = CC[cnt]
            cnt = cnt + 1
            plt.scatter(x_values, y_values, c=COL, s=5, linewidth=1, label=color)
        plt.legend()  # Add legend
        '''
        LEN = min(len(X_Value_rmp),len(X_Value_frp))

        X_Value_rmp = X_Value_rmp[0:LEN]
        X_Value_frp = X_Value_frp[0:LEN]

        fig, ax2 = plt.subplots()

        for data_cnt in range(0,int(len(X_Value_frp)/1)):
            ax2.plot(X_Value_rmp[data_cnt], X_Value_frp[data_cnt],'+b')

        XX = np.array(X_Value_rmp)
        YY = np.array(X_Value_frp)
        print(XX.shape)
        print(YY.shape)

        a, b = np.polyfit(XX[:,0], YY[:,0], 1)

        ax2.plot(XX[:,0], a*XX[:,0]+b,'r')


        #for data_cnt in range(int(len(X_Value_frp)/2),len(X_Value_frp)):
        #    plt.plot(X_Value_rmp[data_cnt], X_Value_frp[data_cnt],'+r')

        ax2.set_xlabel('RPM') 
        ax2.set_ylabel('Fuel Rail Pressure in MPa')
        ax2.grid()

        plt.show()


