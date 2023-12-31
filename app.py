from flask import Flask  , render_template,request,make_response,jsonify,url_for,redirect,Response
import numpy as np
import pandas as pd
import operator
import requests
from pyDecision.algorithm import mabac_method
import json
from flask_cors import CORS
from pyDecision.algorithm import edas_method
from pymcdm.methods import MABAC
from pyDecision.algorithm import ahp_method


# AHP
weight_derivation = 'geometric' # 'mean' or 'geometric'


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


@app.route("/rank-mabac" , methods=['POST'])
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
    df_excluded["test_date"] = df_excluded["test_date"].replace(2018,1)
    df_excluded["test_date"] = df_excluded["test_date"].replace(2019,2)
    df_excluded["test_date"] = df_excluded["test_date"].replace(2020,3)
    df_excluded["test_date"] = df_excluded["test_date"].replace(2021,4)
    df_excluded["test_date"] = df_excluded["test_date"].replace(2022,5)
    print(df_excluded["test_date"])
    print(df_excluded)
    df_converted = df_excluded.astype(float)



    dataset = df_converted.values
    print("dataset")
    print(df_excluded)
    
    weights = np.array([0.1, 0.1, 0.1, 0.1, 0.1,0.1,0.1,0.1,0.1,0.1])

    types = np.array([1, 1,-1,1,1,1,1,1,1,1])

    mabac = MABAC()

    pref = mabac(dataset, weights, types)
    print("rank score:")

    

    print(np.round(pref, 4))

    rank = np.array(np.round(pref, 4))

    final_rank=[]

    for i in range(0,len(rank)):
        final_rank.append({
            "gpu_id":int(gpuId[i]),
            "gpu_name":gpuName[i],
            "price": str(price[i]),
            "alternative":'a' + str(i+1),
            "memSize": str(memSize[i]),
            "mem_clock": str(mem_clock[i]),
            "gpu_clock": str(gpu_clock[i]),
            "score":rank[i]
        })

    print(final_rank)

    sorted_list = sorted(final_rank, key=lambda x: x['score'], reverse=True)

    send_data = json.dumps(sorted_list)

    return send_data

    # return "done"
@app.route("/ahp" , methods=['POST'])
def ahp():
    dataset = np.array([
    [1, 3, 5, 7, 9, 2],
    [1/3, 1, 2, 4, 3, 1],
    [1/5, 1/2, 1, 2, 4, 1/2],
    [1/7, 1/2, 1/2, 1, 2, 1/3],
    [1/9, 1/3, 1/4, 1/2, 1, 1/5],
    [1/2, 1, 2, 3, 5, 1]])

    # Call AHP Function
    weights, rc = ahp_method(dataset, wd = weight_derivation)

    # Weigths
    for i in range(0, weights.shape[0]):
        print('w(g'+str(i+1)+'): ', round(weights[i], 3))
    
    # Consistency Ratio
    print('RC: ' + str(round(rc, 2)))
    if (rc > 0.10):
        print('The solution is inconsistent, the pairwise comparisons must be reviewed')
        return('The solution is inconsistent, the pairwise comparisons must be reviewed')
    else:
        print('The solution is consistent')
        return('The solution is consistent')


@app.route("/rank-mabac-standard" , methods=['POST'])
def postMabacStandard():

    dataset = np.array([
    [1, 3, 5, 7, 9, 2],
    [1/3, 1, 2, 4, 3, 1],
    [1/5, 1/2, 1, 2, 4, 1/2],
    [1/7, 1/2, 1/2, 1, 2, 1/3],
    [1/9, 1/3, 1/4, 1/2, 1, 1/5],
    [1/2, 1, 2, 3, 5, 1]])

    weights, rc = ahp_method(dataset, wd = weight_derivation)
    for i in range(0, weights.shape[0]):
        print('w(g'+str(i+1)+'): ', round(weights[i], 3))
    data = request.json['gpu_data']
    df = pd.DataFrame(data)

    # Consistency Ratio
    print('RC: ' + str(round(rc, 2)))
    if (rc > 0.10):
        print('The solution is inconsistent, the pairwise comparisons must be reviewed')
        # return('The solution is inconsistent, the pairwise comparisons must be reviewed')
    else:
        print('The solution is consistent')
        # return('The solution is consistent')

    columns_to_exclude = ['gpu_name', 'category','gpu_id','company','test_date']

    # GPU Name and ID
    gpuName = df["gpu_name"]    
    gpuId = df["gpu_id"]    
    price = df["price"]    
    # memSize = df["memSize"]    
    # mem_clock = df["mem_clock"]    
    # gpu_clock = df["gpu_clock"]    

    df_excluded = df.drop(columns=columns_to_exclude, axis=0)

        # Convert to float
    # df_replace= df_excluded["test_date"].replace(2020,1)
    # df_excluded["test_date"] = df_excluded["test_date"].replace(2018,1)
    # df_excluded["test_date"] = df_excluded["test_date"].replace(2019,2)
    # df_excluded["test_date"] = df_excluded["test_date"].replace(2020,3)
    # df_excluded["test_date"] = df_excluded["test_date"].replace(2021,4)
    # df_excluded["test_date"] = df_excluded["test_date"].replace(2022,5)
    # print(df_excluded["test_date"])
    # print(df_excluded)
    df_converted = df_excluded.astype(float)



    dataset = df_converted.values
    print("dataset")
    # print(df_excluded)
    
    # weights = np.array([0.2, 0.1, 0.3, 0.2, 0.1,0.1])
    # weights = np.array([0.2, 0.1, 0.3, 0.2, 0.1,0.1])

    types = np.array([1, 1,-1,1,1,1])

    mabac = MABAC()

    pref = mabac(dataset, weights, types)
    print("rank score:")

    

    print(np.round(pref, 4))

    rank = np.array(np.round(pref, 4))

    final_rank=[]

    for i in range(0,len(rank)):
        final_rank.append({
            "gpu_id":int(gpuId[i]),
            "gpu_name":gpuName[i],
            "price": str(price[i]),
            "alternative":'a' + str(i+1),
            # "memSize": str(memSize[i]),
            # "mem_clock": str(mem_clock[i]),
            # "gpu_clock": str(gpu_clock[i]),
            "score":rank[i]
        })

    print(final_rank)

    sorted_list = sorted(final_rank, key=lambda x: x['score'], reverse=True)

    send_data = json.dumps(sorted_list)

    return send_data

    # return "done"


@app.route("/rank-edas" , methods=['POST'])
def postEdas():
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