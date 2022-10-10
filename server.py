import os
import json
from flask import Flask, request, render_template, jsonify
from gspread import authorize
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

json_creds = os.getenv("GOOGLE_SHEETS_CREDS_JSON")
creds_dict = json.loads(json_creds)
creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)

acc = authorize(creds)
sh = acc.open("Plantonic-Sensor-Data")
wk = sh.worksheet('temp-hum')

token = os.getenv("DATA_PASS") if os.getenv(
    "DATA_PASS") != None else "Bearer Test"


@app.route("/")
def home():
    data = wk.get("A2:D1000")
    return render_template("data.html", data=data)


@app.route("/data", methods=["POST", "GET"])
def post():
    if (request.method == "GET"):
        return wk.get("A2:D1000")
    auth = request.headers.get("Authorization")
    if (auth == None or auth.split()[1] != token):
        return jsonify({"error": "Invalid Auth Token", "token": auth})
    data = request.get_json()
    print(data)
    reading = [data.get("time"), data.get("temperature"),
               data.get("humidity"), data.get("Sunlight")]
    print(reading)
    if None in reading:
        return jsonify({"error": "Wrong format", "reading": data})
    wk.append_row(reading)
    return jsonify({"status": "successful"})
