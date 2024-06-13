import requests 
import csv
import json
import pandas as pd
from datetime import datetime, timezone
import os
from pathlib import Path





# for US vehicles set the url as "http://algo-internal-apis.intangles-aws-us-east-1.intangles.us:1234/dashboard_apis/fetch"
# for Indian vehicles set the url as "http://internal-apis.intangles.com/dashboard_apis/fetch"

url =  "https://algo-internal-apis.intangles-aws-us-east-1.intangles.us/dashboard_apis/fetch/"

# enter the output path where you want the output to be written
output_path = "D:/Work/FRP/CODE/"


def fetch_dtc_data(start_ts, end_ts, fault_code):
    
    df_all_dtcs = pd.DataFrame()
    start_batch_time = start_ts 
    end_batch_time = start_batch_time + 24*1*60*60*1000 

    
    while end_batch_time <= end_ts:
        print("starting timestamp ", start_batch_time) 
        print("ending timestamp ", end_batch_time)
        headers = {
                'Content-Type': 'application/json',
            }
        vehicle_dtc_data = {"report": "default",
            "filter":[
                {
                    "fault_log.timestamp":{
                        "gt": start_batch_time,
                        "lt": end_batch_time
                    }
                },

                {
                    "fault_log.status": "active"
                },
                {
                    "fault_log.code": fault_code
                }
            ],
            "select":{
                "fault_log.status":{
                    "value":True,
                    "as":"status"
                },
                "fault_log.code":{
                    "value":True,
                    "as":"code"
                },
                "fault_code.severity":{
                    "value":True,
                    "as":"severity"
                },
                "vehicle.id":{
                    "value":True,
                    "as":"vehicle_id"
                },
                "fault_log.vehicle_id":{
                    "value":True,
                    "as":"vehicle_id1"
                },
                "vehicle.account_id": {
                    "value": True,
                    "as": "account_id"
                },
                "vehicle.tag":{
                    "value":True,
                    "as":"vehicle_plate"
                },
                "fault_log.timestamp":{
                    "value":True,
                    "as":"time"
                },
                "spec.manufacturer":{
                    "value":True,
                    "as":"manufacturer"
                },
                "spec.max_load_capacity":{
                    "value":True,
                    "as": "max_load_capacity"
                },
                "fault_code.description":{
                    "value":True,
                    "as":"description"
                }
            }
            }
   
        dtc_response = requests.post(url, json=vehicle_dtc_data, headers=headers)
        print(dtc_response)
        dtc_csv_filename = 'dtc.csv'
        if dtc_response.status_code == 200:
            # Parse the JSON response
            dtc_json_data = dtc_response.json()
            dtc_headers = dtc_json_data['result']['fields']
            with open(dtc_csv_filename, 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=dtc_headers)
                
                # Write headers to the CSV file
                csv_writer.writeheader()
                
                # Write each JSON item as a row in the CSV file
                csv_writer.writerows(dtc_json_data['result']['output'])
        else:
            print(f"Failed to fetch the dtc data. Status code: {dtc_response.status_code}")
        df_dtc = pd.read_csv(dtc_csv_filename, encoding='unicode_escape') 

        start_batch_time += 24*1*60*60*1000 
        end_batch_time = start_batch_time + 24*1*60*60*1000

        df_all_dtcs= pd.concat([df_all_dtcs, df_dtc], ignore_index=True)

    return df_all_dtcs



def miliseconds_to_utc(time_ms):
    time_seconds = time_ms / 1000.0
    # Create a UTC datetime object
    trip_time_utc = datetime.utcfromtimestamp(time_seconds).replace(tzinfo=timezone.utc)
    formatted_trip_time_utc = trip_time_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    return formatted_trip_time_utc

def utc_to_miliseconds(utc_date_string):
    # Parse the UTC date string into a datetime object
    utc_datetime = datetime.strptime(utc_date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    # Convert seconds to milliseconds
    milliseconds = int(utc_datetime.timestamp() * 1000)

    return milliseconds

# enter the start time and end time between which you want the dtc
start_ts =  1713632761360
end_ts =    1718166929201
fault_code = "P0088"


df_dtc = fetch_dtc_data(start_ts, end_ts, fault_code)
df_dtc = df_dtc.drop_duplicates(keep='first')
df_dtc['time_miliseconds'] = df_dtc['time'].apply(utc_to_miliseconds)

df_dtc = df_dtc.drop_duplicates()

df_dtc.to_csv(output_path + "dtc.csv") 