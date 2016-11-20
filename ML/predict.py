import requests
import json
import math
from sklearn.externals import joblib
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np

arrivalRegNew = joblib.load('model.pkl')
enc = joblib.load('enc1.pkl')
lbl_text = joblib.load('enc2.pkl')
enc1 = joblib.load('enc3.pkl')
lbl_text1 = joblib.load('enc4.pkl')


def predit(start, end, hour, minutes):
    returnArr = []
    try:
        BASE_URL_CON = "http://transport.opendata.ch/v1/connections"
        r = requests.get(
            BASE_URL_CON + '?' + "from=" + start + "&to=" + end + "&time=" + str(hour) + ":" + str(minutes))
        response = json.loads(r.text)
        for i in range(0, len(response['connections'][0]['sections'])):
            # print(response['connections'][0]['sections'][i]['departure']['location']['name'])
            # print(response['connections'][0]['sections'][i]['arrival']['location']['name'])
            # print(response['connections'][0]['sections'][i]['journey']['category'])
            # print(response['connections'][0]['sections'][i]['journey']['number'])
            LINIEN_TEXT = pd.DataFrame(enc.transform(
                lbl_text.transform(response['connections'][0]['sections'][i]['journey']['category']).reshape(-1,
                                                                                                             1)).toarray())
            HALTESTELLEN_NAME = pd.DataFrame(enc1.transform(
                lbl_text1.transform(response['connections'][0]['sections'][i]['arrival']['location']['name']).reshape(
                    -1, 1)).toarray())
            x_test = pd.concat(
                [pd.DataFrame([response['connections'][0]['sections'][i]['journey']['number']]), LINIEN_TEXT,
                 HALTESTELLEN_NAME], axis=1)
            # print(x_test)
            time = math.floor(arrivalRegNew.predict(x_test) / 60)
            # print(time)
            if (time < 0):
                time = time * (-1)
                returnArr.append(
                    "Your train form " + response['connections'][0]['sections'][i]['departure']['location'][
                        'name'] + " to " + response['connections'][0]['sections'][i]['arrival']['location'][
                        'name'] + " is expected to arrive " + str(time) + " minutes late.")
            elif (time > 0):
                returnArr.append(
                    "Your train form " + response['connections'][0]['sections'][i]['departure']['location'][
                        'name'] + " to " + response['connections'][0]['sections'][i]['arrival']['location'][
                        'name'] + " is expected to arrive " + str(time) + "is expected to arrive " + str(
                        time) + " minutes early.")
            else:
                returnArr.append(
                    "Your train form " + response['connections'][0]['sections'][i]['departure']['location'][
                        'name'] + " to " + response['connections'][0]['sections'][i]['arrival']['location'][
                        'name'] + " is expected to arrive " + str(time) + "is expected to arrive on time.")
        return returnArr
    except:
        returnArr.append("Ooops looks like we encourted an error")
        return returnArr
