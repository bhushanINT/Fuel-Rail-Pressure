import numpy as np
from matplotlib import pyplot as plt 
import os
import json

def extract_PID_data(data, PROTOCOL,LABEL):
    
    if (PROTOCOL == 'SAE'):

        if LABEL == 'IMAP':
            PID_TAG = '106'
        elif LABEL == 'ENGINE LOAD':
            PID_TAG = '92'
        elif LABEL == 'OIL PRESSURE':
            PID_TAG = '100'
        elif LABEL == 'ENGINE RPM':
            PID_TAG = '190'
        elif LABEL == 'FUEL RATE':
            PID_TAG = '183'
        elif LABEL == 'MAF':
            PID_TAG = '132'
        elif LABEL == 'BOOST':
            PID_TAG = '102'
        elif LABEL == 'BAROMETER':
            PID_TAG = '108'
        elif LABEL == 'THROTTLE':
            PID_TAG = '91'
        elif LABEL == 'ATGMF': # Eaxuast Gas Flow Rate
            PID_TAG = '3236'
        elif LABEL == 'DPFDP': # DPF Diffrential Pressure (across DPF)
            PID_TAG = '7ABC'#'3251'
            #PID_TAG = '3251'
        elif LABEL == 'SCRT':   # SCR Catalyst Temperature Before Catalyst (DPF out)
            PID_TAG = '4360'
        elif LABEL == 'SPEED': # Wheep based Vehicle Speed
            PID_TAG = '84'
        elif LABEL == 'DPFINT':# DPF in Temperature Before DPF (DOC out)
            #PID_TAG = '4766' #4766 #3250
            #PID_TAG = '3250' #4766 #3250
            PID_TAG = '7CBC' #4766 #3250
        elif LABEL == 'IS': #  regen inhibited
            PID_TAG = '3703'        
        elif LABEL == 'FUEL USE': #  Total fuel used (high precision)
            PID_TAG = '5054'        
        elif LABEL == 'DISTANCE': #  Total distance travelled (high precision)
            PID_TAG = '917' # 245
        elif LABEL == 'SOOTLOAD':
            PID_TAG = '5466' # 245 #3719 generic check       
        elif LABEL == 'ACTIVEREGEN':
            PID_TAG = '3700' # 245

    elif(PROTOCOL == 'ISO'):

        if LABEL == 'IMAP':
            PID_TAG = '87BC'#MODIFY the "if PID_TAG in State1:" loop (append for loop on top)  
        elif LABEL == 'ENGINE LOAD':
            PID_TAG = '04'
        elif LABEL == 'ENGINE RPM':
            PID_TAG = '0C'
        elif LABEL == 'FUEL RATE':
            PID_TAG = '5E'
        elif LABEL == 'MAF':
            PID_TAG = '10'
        elif LABEL == 'BOOST':
            PID_TAG = '102'
        elif LABEL == 'BAROMETER':
            PID_TAG = '33'
        elif LABEL == 'THROTTLE':
            PID_TAG = '11'#MODIFY the "if PID_TAG in State1:" loop (append for loop on top)
        elif LABEL == 'DPFDP': # DPF Diffrential Pressure (across DPF)
            PID_TAG = '7A'

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

    V_ID = '941321887898664960' #(P0192)
    A_TS=[1652491611000,1652504237000,1652527999000,1652928359000,1653241376000,1653255863000,1653324431000,1653359125000,1653423518000,1653426094000,1653433961000,1653453042000,1653478128000,1653515623000,1653535777000]
    R_TS=[1652492027000,1652520583000,1652536935000,1652950329000,1653250828000,1653298909000,1653353710000,1653384812000,1653424950000,1653433024000,1653443050000,1653473976000,1653508753000,1653531840000,1653542290000]

    #V_ID = '897734910595301376' #(P0193)
    #A_TS=[1660666909000,1660840040000,1661157779000,1661183959000,1661134886000,1661316002000,1661235314000]
    #R_TS=[1660702409000,1661013427000,1661154061000,1661264638000,1661233241000,1661170009000,1661338822000]

    dir_list = os.listdir('D:/Work/FRP/DATA/'+ V_ID + '/')

    PROTOCOL = 'SAE'

    FLAG = 0
    LABEL = 'FUEL RATE'

    for file in dir_list:
        print("Viechle ID-------", file)
        OBD_data_path = 'D:/Work/FRP/DATA/'+ V_ID +'/' + file
        OBD_data = [json.loads(line) for line in open(OBD_data_path, 'r')]
        X_Time, X_Value = extract_PID_data(OBD_data,PROTOCOL,LABEL)
        print(len(X_Value))

        if ((len(X_Value[0])>0) and (FLAG==0)):
            DATA = np.array(X_Value)
            T = np.array(X_Time) 
            FLAG = 1
        else:
            if(len(X_Value[0])>0):
                DATA = np.concatenate((DATA,np.array(X_Value)),axis=0)
                T = np.concatenate((T,np.array(X_Time)),axis=0)


    fig, ax1 = plt.subplots()
    ax1.plot(T,DATA,'.b')
    for cnt in range (0,len(A_TS)):
        ax1.axvline(x = A_TS[cnt] , ymin=0, ymax=3, color='r')
        ax1.axvline(x = R_TS[cnt] , ymin=0, ymax=3, color='g')

    plt.show()