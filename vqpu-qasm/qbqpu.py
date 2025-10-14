import json
import requests
import time
import os
import ast
import ssl
import certifi
import urllib
import urllib3
from urllib.request import urlopen
import subprocess
from collections import Counter

# qcstack uses self-signed certs, so do not verify secure connection by default.
verify_ssl=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#check if circuit execution is finished and return response
def get_experiment_status(id:int, qpu_url:str):
    url = qpu_url+"/api/v2/circuits/"+str(id)
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers, verify=verify_ssl)
    return response

#given circuit (string) array and shot count, send an experiment to qcstack API and return response
def send_experiment(circuit, shots, qpu_url:str):
    headers = {'Content-Type': 'application/json'}
    json_data = {'circuit': circuit,'shots': shots}
    response = requests.post(qpu_url+"/api/v2/circuits/openqasm2", headers=headers, json=json_data, verify=verify_ssl)
    return response
    
#full pipeline to run an experiment including
#(1) sending task to qcstack API
#(2) obtaining experiment id and checking for solutions every polling_time secs for a maximum of max_requests times
#(3) on success, return final json data
def run_experiment(circuit, shots:int, qpu_url:str, polling_time = 10, max_requests = 1000):
    #(1) send experiment to qcstack API and get response 
    send_response = send_experiment(circuit, shots, qpu_url)
    if send_response.status_code != 200:
        print("An error occured while sending experiment to qcstack!")
        print(send_response)
        print(send_response.json())
        return None
    #(2) on success, obtain experiment id and try to obtain results
    experiment_id = send_response.json()['id']
    print("Experiment was sent to qcstack API. ID is " + str(experiment_id))
    request_idx = 0
    while request_idx < max_requests:
        request_idx += 1
        response = get_experiment_status(experiment_id, qpu_url)
        if response.status_code == 200: #experiment successfully completed 
            print("Execution terminated at request #" + str(request_idx))
            return response.json()
        elif response.status_code == 425: #polling to early 
            print("Request " + str(request_idx) + "/" + str(max_requests) + ": too early, wait for " + str(polling_time) + " seconds!")
            time.sleep(polling_time)
        else:
            print("Request " + str(request_idx) + "/" + str(max_requests) + ": an error occured!")
            print(response)
            print(response.json())
            return None

def get_bitstring_counts(response):
    f = lambda x: "".join(map(str,x))
    bitstrings = list(map( f, response["data"]))
    return dict(Counter(bitstrings))
