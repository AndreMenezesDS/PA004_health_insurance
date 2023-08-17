import os

import pickle
import pandas as pd
from flask import Flask, Response, request
from health_insurance.HealthInsurance import HealthInsurance

#loading model
model = pickle.load(open('src/models/model_health_insurance.pkl', 'rb'))

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def health_insurance_predict():
    test_json = request.get_json()

    if test_json: #there is data
        if isinstance(test_json, dict): #unique example
            test_raw = pd.DataFrame(test_json, index=[0])
        else: #multiple examples
            test_raw = pd.DataFrame(test_json, columns=test_json[0].keys())

        #Instantiate Health Insurance Class
        pipeline = HealthInsurance()

        #Data Cleaning
        df1 = pipeline.data_cleaning(test_raw)

        #Reorder Data
        df2 = pipeline.reorder_data(df1)

        #Feature Engineering
        df3 = pipeline.feature_engineering(df2)

        #Data Preparation
        df4 = pipeline.data_preparation(df3)

        #Prediction
        df_response = pipeline.get_prediction(model, test_raw, df4)

        return df_response
    
    else:
        return Response( '{}', status=200, mimetype='application/json')
    
if __name__ == '__main__':
    port = os.environ.get('PORT' ,5000)
    app.run('0.0.0.0', debug=True)