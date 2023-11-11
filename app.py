from flask import Flask  , render_template,request,make_response,jsonify,url_for,redirect,Response
# import numpy as np
import pandas as pd
import operator
import requests
from pyDecision.algorithm import mabac_method
import json
from flask_cors import CORS


# Benefit or Cost
criterion_type = ['max', 'max', 'min', 'max', 'max', 'max']



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:8000"}}) 

@app.route("/test" , methods=['GET'])
def testing():
    return "hello"


@app.route("/post-rank" , methods=['POST'])
def postRank():
    data = request.json['gpu_data']
    print(data)
    # return "data posted"
    # user = request.json['user']
    # print(user)

    df = pd.DataFrame(data)

    columns_to_exclude = ['gpu_name', 'test_date', 'category','gpu_id','company']

    # GPU Name and ID
    gpuName = df["gpu_name"]    
    gpuId = df["gpu_id"]    

    df_excluded = df.drop(columns=columns_to_exclude, axis=0)

        # Convert to float
    df_converted = df_excluded.astype(float)

    dataset = df_converted.values

        # Ranking Begin
    rank = mabac_method(dataset, criterion_type, graph = False, verbose = False)

    final_rank=[]

        #Append to new Array with GPU Name
    for i in range(0, rank.shape[0]):
        final_rank.append({
            "gpuId":int(gpuId[i]),
            "gpuName":gpuName[i],
            "alternative":'a' + str(i+1),
            "score":round(rank[i], 4)
        })

    sorted_list = sorted(final_rank, key=lambda x: x['score'], reverse=True)

    send_data = json.dumps(sorted_list)

        # headers = {
        #     'Content-Type': 'application/json'
        # }

        # postresponse = requests.post('http://127.0.0.1:8000/api/gpu',data=send_data,headers=headers)
        #         # Handling the response
        # if response.status_code == 200:
        #     # Successful request
        #     response_data = response.json()  # If the response is in JSON format
        #     print("Response:", response_data)
        # else:
        #     # Failed request
        #     print("Request failed with status code:", response.status_code)

    return send_data


    # return "hello" 

@app.route("/" , methods=['GET'])
def index():
    if request.method == "GET":
        # API Request
        response = requests.get('http://127.0.0.1:8000/api/gpu')
        # response = requests.get('http://192.168.1.10:8000/api/gpu')
        #response = requests.get('https://sirefis-backend.vercel.app/gpu2020')
        
        

        responseJson = response.json()

        # Data Frame Start
        df = pd.DataFrame(responseJson)

        columns_to_exclude = ['gpu_name', 'test_date', 'category','gpu_id']
        #columns_to_exclude = ['gpuName', 'testDate', 'category','gpuId']

        # GPU Name
        gpuName = df["gpu_name"]    

        df_excluded = df.drop(columns=columns_to_exclude, axis=0)

        # Convert to float
        df_converted = df_excluded.astype(float)

        dataset = df_converted.values

        # Ranking Begin
        rank = mabac_method(dataset, criterion_type, graph = False, verbose = False)

        final_rank=[]

        #Append to new Array with GPU Name
        for i in range(0, rank.shape[0]):
            final_rank.append({
                "gpuName":gpuName[i],
                "alternative":'a' + str(i+1),
                "score":round(rank[i], 4)
            })

        sorted_list = sorted(final_rank, key=lambda x: x['score'], reverse=True)

        send_data = json.dumps(sorted_list)

        # headers = {
        #     'Content-Type': 'application/json'
        # }

        # postresponse = requests.post('http://127.0.0.1:8000/api/gpu',data=send_data,headers=headers)
        #         # Handling the response
        # if response.status_code == 200:
        #     # Successful request
        #     response_data = response.json()  # If the response is in JSON format
        #     print("Response:", response_data)
        # else:
        #     # Failed request
        #     print("Request failed with status code:", response.status_code)

        return send_data



        

if __name__ == "__main__":
    app.run()