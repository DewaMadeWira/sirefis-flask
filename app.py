from flask import Flask  , render_template,request,make_response,jsonify,url_for,redirect,Response
# import numpy as np
import pandas as pd
import operator
import requests
from pyDecision.algorithm import mabac_method
import json
from flask_cors import CORS
from pyDecision.algorithm import edas_method


# Benefit or Cost
criterion_type = ['max', 'max', 'min', 'max', 'max', 'max']
criterion_type_edas = ['max', 'max', 'min', 'max', 'max', 'max','max','max','max','max']
weights = [0.1, 0.1, 0.15, 0.1, 0.1,0.1,0.1,0.1,0.1,0.05]


app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:8000"}}) 
CORS(app) 

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
    price = df["price"]    

    df_excluded = df.drop(columns=columns_to_exclude, axis=0)

        # Convert to float
    df_converted = df_excluded.astype(float)

    dataset = df_converted.values
    print("dataset")
    print(dataset)
    

        # Ranking Begin
    rank = mabac_method(dataset, criterion_type, graph = False, verbose = True)

    final_rank=[]

        #Append to new Array with GPU Name
    for i in range(0, rank.shape[0]):
        final_rank.append({
            "gpu_id":int(gpuId[i]),
            "gpu_name":gpuName[i],
            "price": str(price[i]),
            "alternative":'a' + str(i+1),
            "score":round(rank[i], 4)
        })

    sorted_list = sorted(final_rank, key=lambda x: x['score'], reverse=True)

    send_data = json.dumps(sorted_list)

    return send_data


@app.route("/rank-edas" , methods=['POST'])
def postMabac():
    data = request.json['gpu_data']
    df = pd.DataFrame(data)

    columns_to_exclude = ['gpu_name', 'category','gpu_id','company']

    # GPU Name and ID
    gpuName = df["gpu_name"]    
    gpuId = df["gpu_id"]    
    price = df["price"]    
    memSize = df["memSize"]    
    mem_clock = df["mem_clock"]    
    gpu_clock = df["gpu_clock"]    

    df_excluded = df.drop(columns=columns_to_exclude, axis=0)

        # Convert to float
    # df_replace= df_excluded["test_date"].replace(2020,1)
    df_excluded["test_date"] = df_excluded["test_date"].replace(2020,1)
    df_excluded["test_date"] = df_excluded["test_date"].replace(2021,2)
    df_excluded["test_date"] = df_excluded["test_date"].replace(2022,3)
    print(df_excluded["test_date"])
    print(df_excluded)
    df_converted = df_excluded.astype(float)



    dataset = df_converted.values
    print("dataset")
    print(df_excluded)

    

    # Ranking Begin
    # rank = mabac_method(dataset, criterion_type_edas, graph = False, verbose = True)
    rank = edas_method(dataset, criterion_type_edas, weights, graph = False, verbose = True)

    final_rank=[]

        #Append to new Array with GPU Name
    for i in range(0, rank.shape[0]):
        final_rank.append({
            "gpu_id":int(gpuId[i]),
            "gpu_name":gpuName[i],
            "price": str(price[i]),
            "alternative":'a' + str(i+1),
            "memSize": str(memSize[i]),
            "mem_clock": str(mem_clock[i]),
            "gpu_clock": str(gpu_clock[i]),
            "score":round(rank[i], 4)
        })

    sorted_list = sorted(final_rank, key=lambda x: x['score'], reverse=True)

    send_data = json.dumps(sorted_list)

    return send_data

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
       

        # GPU Name
        gpuName = df["gpu_name"]    

        df_excluded = df.drop(columns=columns_to_exclude, axis=0)

        # Convert to float
        df_converted = df_excluded.astype(float)

        dataset = df_converted.values

        # Ranking Begin
        rank = edas_method(dataset, criterion_type, graph = False, verbose = False)

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