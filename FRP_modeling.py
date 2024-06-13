import numpy as np
import pandas as pd
import json
from matplotlib import pyplot as plt 
from scipy.stats import norm
from utils_FRP import extract_PID_data,resample_PID_data,RPM_Contraint,Engine_load_Contraint
import os
from scipy import stats

from sklearn.mixture import GaussianMixture as GMM


# Extract configuration informatioon
VARIABLES = ["FRP","ENGINE RPM","THROTTLE","ENGINE LOAD", "SPEED"]
RPM_RANGE = [1000, 1800] 
ENGINE_LOAD_CUTOFF = 0

# Data Read
#OBD_data_path = 'D:/Work/FRP/DATA/WITH_157/1242065884269248512'
#OBD_data_path = 'D:/Work/Timeseries_models/DATA/TH_DATA/EBT/T/1225921763074899968'
OBD_data_path = 'D:/Work/FRP/DATA/FOTA/EBT/Kenworth - Cummins ISX/1281757509668831232'


FLAG = 0

for data_packet_cnt in range(0,1):
    OBD_data = [json.loads(line) for line in open(OBD_data_path, 'r')]
    T_L = []
    V_L = []
    # EXtract Required PIDs from Jason
    for var_type in VARIABLES:
        X_Time, X_Value = extract_PID_data(OBD_data,'SAE_AVG',var_type, 0)
        T_L.append(np.array((X_Time), dtype=np.int64))
        V_L.append(np.array((X_Value), dtype=float))
    if (len(V_L[0]) > 0):

        Temp_time = np.array(T_L[1]) # its DP time so no need to resample
        Resample_data = resample_PID_data(V_L,len(VARIABLES)) # Resample other PIDs w.r.t DP

        if ((len(V_L[0])>0) and (FLAG==0)):
            DATA = Resample_data
            T1 = Temp_time 
            FLAG = 1
        else:
            if(len(V_L[0])>0):
                DATA = np.concatenate((DATA,Resample_data),axis=1)
                T1 = np.concatenate((T1,Temp_time),axis=0)

#print(DATA.shape)

X_1,T2 = RPM_Contraint(DATA,T1,np.array(RPM_RANGE))
X_2,T3 = Engine_load_Contraint(X_1,T2,ENGINE_LOAD_CUTOFF)

Num_bin = 5
Step =  int((RPM_RANGE[1]-RPM_RANGE[0])/Num_bin)

FRP_TEMP = X_2[0,:] # 1st is FRP
RPM_TEMP = X_2[1,:] # 1st is FRP
#print(FRP_TEMP.shape)

bin_cnt = 0
MODEL_MAT = np.zeros((5,2))


for rpm_bin in range(RPM_RANGE[0],RPM_RANGE[1],Step):
    Bin_Samples = FRP_TEMP[(rpm_bin < RPM_TEMP) & (RPM_TEMP <= rpm_bin+Step)]
    print(Bin_Samples.shape)
    #fig, ax1 = plt.subplots()
    #ax1.plot(Bin_Samples,'b')

    #set the lower and higher percentile range
    lower_percentile = np.percentile(Bin_Samples, 5)
    higher_percentile = np.percentile(Bin_Samples, 95)
    #cap values below low to low
    print(Bin_Samples.shape)
    Bin_Samples  = np.delete(Bin_Samples, (lower_percentile > Bin_Samples))
    Bin_Samples  = np.delete(Bin_Samples, (higher_percentile < Bin_Samples))
    # | (Bin_Samples > higher_percentile)
    print(Bin_Samples.shape)

    #https://towardsdatascience.com/the-basics-of-anomaly-detection-65aff59949b7
    #https://towardsdatascience.com/understanding-anomaly-detection-in-python-using-gaussian-mixture-model-e26e5d06094b
    #https://udohsolomon.github.io/_posts/2017-09-12-Anomaly-detection/
    #means = np.mean(Bin_Samples)
    #stdevs = np.std(Bin_Samples)
    #dist = stats.norm(means, stdevs)
    #proba = dist.pdf(np.array(123+8).T)
    #print(proba)


    # best fit of data
    (mu, sigma) = norm.fit(Bin_Samples)
    print("Min----------------------->",np.min(Bin_Samples))
    print("Max----------------------->",np.max(Bin_Samples))
    print("Mean----------------------->",mu)
    print("Std----------------------->",sigma)
    #plt.hist(Bin_Samples, bins=100, color='skyblue', edgecolor='black')
    #plt.xlabel('Values')
    #plt.ylabel('Frequency')
    #plt.title('Basic Histogram')
    #plt.show()
    MODEL_MAT[bin_cnt,0] = mu
    MODEL_MAT[bin_cnt,1] = sigma
    bin_cnt = bin_cnt + 1

#exit(0)

'''
    # create GMM model object
    #https://www.geeksforgeeks.org/gaussian-mixture-model/
    #https://stackoverflow.com/questions/55187037/how-can-i-do-a-histogram-with-1d-gaussian-mixture-with-sklearn
    x = Bin_Samples.reshape(-1,1)
    gmm = GMM(n_components = 2, max_iter=1000, random_state=10, covariance_type = 'full')
    mean = gmm.fit(x).means_ 
    print("mean----------------------->",mean)
    covs  = gmm.fit(x).covariances_
    print("covs----------------------->",covs)
    weights = gmm.fit(x).weights_
    print("weights----------------------->",weights)
'''
    # the histogram of the data
    #fig, ax2 = plt.subplots()
    #n, bins, patches = ax2.hist(Bin_Samples, 60)
    # add a 'best fit' line
    #y = norm.pdf( bins, mu, sigma)
    #l = ax2.plot(bins, 4000*y, 'r--', linewidth=2)
    #plt.show()
    #exit(0)


#Matching logic for 5 bins:
# 1st Bucket mean B_Mean and B_Std 
# for Lowest bin find mean of FRP (M_FRP)...it should be ((B_Mean-(B_Std/1)) < M_FRP < (B_Mean+(B_Std/5)))

# 2nd Bucket mean B_Mean and B_Std 
# for Lowest bin find mean of FRP (M_FRP)...it should be ((B_Mean-(B_Std/2)) < M_FRP < (B_Mean+(B_Std/4)))

# 3rd Bucket mean B_Mean and B_Std 
# for Lowest bin find mean of FRP (M_FRP)...it should be ((B_Mean-(B_Std/3)) < M_FRP < (B_Mean+(B_Std/3)))

# 4th Bucket mean B_Mean and B_Std 
# for Lowest bin find mean of FRP (M_FRP)...it should be ((B_Mean-(B_Std/4)) < M_FRP < (B_Mean+(B_Std/2)))

# 5th Bucket mean B_Mean and B_Std 
# for Lowest bin find mean of FRP (M_FRP)...it should be ((B_Mean-(B_Std/5)) < M_FRP < (B_Mean+(B_Std/1)))


# if more than 2 fails then minor alert ...more than that Major 

#The natural distribution of data can sometimes help you identify outliers. 
#One of the most common assumptions about data distribution is that it follows a Gaussian (or normal) distribution. 
#In a perfectly Gaussian distribution, about 68% of the data lies within one standard deviation from the mean, 
#95% within two standard deviations, and 99.7% within three standard deviations. 
#Data points that fall far away from the mean (typically beyond three standard deviations) can be considered outliers.

########################TESTING##################################
Win_size = 200
std_scale = 2
for Win_cnt in range(0,X_2.shape[1],Win_size):
    TEMP = X_2[0,Win_cnt:Win_cnt+Win_size]
    RPM_TEMP = X_2[1,Win_cnt:Win_cnt+Win_size]
    bin_cnt = 0
    for rpm_bin in range(RPM_RANGE[0],RPM_RANGE[1],Step):
        Bin_Samples = TEMP[(rpm_bin < RPM_TEMP) & (RPM_TEMP <= rpm_bin+Step)]
        print(len(Bin_Samples))
        if (len(Bin_Samples)>0):
            B_Mean = np.mean(Bin_Samples)
        else:
            B_Mean = 0 

        if((B_Mean>0) & (bin_cnt==0)):
            #if(((MODEL_MAT[bin_cnt,0]-(MODEL_MAT[bin_cnt,1]/1)) < B_Mean < (MODEL_MAT[bin_cnt,0]+(MODEL_MAT[bin_cnt,1]/5)))):
            if(((MODEL_MAT[bin_cnt,0]-(MODEL_MAT[bin_cnt,1]*std_scale)) < B_Mean < (MODEL_MAT[bin_cnt,0]+(MODEL_MAT[bin_cnt,1]*std_scale)))): #multiply second trem by 3 (above text) or /0.33                print('...............................GOOD')
                    print('...............................GOOD') 
            else:
                if(B_Mean < MODEL_MAT[bin_cnt,0]):
                    print('...............................ALERT P0087')
                else:
                    print('...............................ALERT P0088')
        elif((B_Mean>0) & (bin_cnt==1)):
            #if(((MODEL_MAT[bin_cnt,0]-(MODEL_MAT[bin_cnt,1]/2)) < B_Mean < (MODEL_MAT[bin_cnt,0]+(MODEL_MAT[bin_cnt,1]/4)))):
            if(((MODEL_MAT[bin_cnt,0]-(MODEL_MAT[bin_cnt,1]*std_scale)) < B_Mean < (MODEL_MAT[bin_cnt,0]+(MODEL_MAT[bin_cnt,1]*std_scale)))):
                print('...............................GOOD')
            else:
                if(B_Mean < MODEL_MAT[bin_cnt,0]):
                    print('...............................ALERT P0087')
                else:
                    print('...............................ALERT P0088')
        elif((B_Mean>0) & (bin_cnt==2)):
            #if(((MODEL_MAT[bin_cnt,0]-(MODEL_MAT[bin_cnt,1]/3)) < B_Mean < (MODEL_MAT[bin_cnt,0]+(MODEL_MAT[bin_cnt,1]/3)))):
            if(((MODEL_MAT[bin_cnt,0]-(MODEL_MAT[bin_cnt,1]*std_scale)) < B_Mean < (MODEL_MAT[bin_cnt,0]+(MODEL_MAT[bin_cnt,1]*std_scale)))):
                print('...............................GOOD')
            else:
                if(B_Mean < MODEL_MAT[bin_cnt,0]):
                    print('...............................ALERT P0087')
                else:
                    print('...............................ALERT P0088')
        elif((B_Mean>0) & (bin_cnt==3)):
            #if(((MODEL_MAT[bin_cnt,0]-(MODEL_MAT[bin_cnt,1]/4)) < B_Mean < (MODEL_MAT[bin_cnt,0]+(MODEL_MAT[bin_cnt,1]/2)))):
            if(((MODEL_MAT[bin_cnt,0]-(MODEL_MAT[bin_cnt,1]*std_scale)) < B_Mean < (MODEL_MAT[bin_cnt,0]+(MODEL_MAT[bin_cnt,1]*std_scale)))):
                print('...............................GOOD')
            else:
                if(B_Mean < MODEL_MAT[bin_cnt,0]):
                    print('...............................ALERT P0087')
                else:
                    print('...............................ALERT P0088')
        elif((B_Mean>0) & (bin_cnt==4)):
            #if(((MODEL_MAT[bin_cnt,0]-(MODEL_MAT[bin_cnt,1]/5)) < B_Mean < (MODEL_MAT[bin_cnt,0]+(MODEL_MAT[bin_cnt,1]/1)))):
            if(((MODEL_MAT[bin_cnt,0]-(MODEL_MAT[bin_cnt,1]*std_scale)) < B_Mean < (MODEL_MAT[bin_cnt,0]+(MODEL_MAT[bin_cnt,1]*std_scale)))):
                print('...............................GOOD')
            else:
                if(B_Mean < MODEL_MAT[bin_cnt,0]):
                    print('...............................ALERT P0087')
                else:
                    print('...............................ALERT P0088')
        else:
            print('...............................BIN EMPTY')

        bin_cnt =  bin_cnt + 1
    print('****************************************************************************************************')

    






