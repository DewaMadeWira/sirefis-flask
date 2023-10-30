from flask import Flask  , render_template,request,make_response,jsonify,url_for,redirect,Response
import numpy as np
import pandas as pd
import operator
import requests
from pyDecision.algorithm import mabac_method
import json

# Benefit or Cost
criterion_type = ['max', 'max', 'min', 'max', 'max', 'max']



app = Flask(__name__)

@app.route("/" , methods=['GET'])
def index():
    # if request.method == "GET":
    #     return jsonify({'name':'Jimit',
    #                 'address':'India'})
    if request.method == "GET":
        # API Request
        response = requests.get('https://sirefis-backend.vercel.app/gpu2020')

        responseJson = response.json()

        # Data Frame Start
        df = pd.DataFrame(responseJson)

        columns_to_exclude = ['gpuName', 'testDate', 'category','gpuId']

        # GPU Name
        gpuName = df["gpuName"]

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

        return send_data



        

if __name__ == "__main__":
    app.run()