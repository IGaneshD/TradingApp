from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import pandas as pd
import json
import sys
from pathlib import Path

# Create your views here.

# This project is coded by 
# `Ganesh Deshmukh`
# This is a Assessment Project 
# for Neiha Business Technologies

# candle Class Definition
class Candle:
    def __init__(self, candle_value):
        self.id = candle_value['id']
        self.date = candle_value['date']
        self.open = candle_value['open']
        self.high = candle_value['high']
        self.low = candle_value['low']


def convert_to_json(converted_candles,filename, timeFrame):
    generatedfilename = 'staticfiles/generatedJson' + filename + timeFrame + '.json'
    with open(generatedfilename, 'w') as json_file:
        json.dump([candle.__dict__ for candle in converted_candles], json_file)

    return generatedfilename

def Candles_to_TimeFrame(candle_objects, timeFrame):
    # create Candles from given TimeFrame
    converted_candles = []
    current_time = 0
    current_candle = None
    current_timeFrame_High = -sys.maxsize
    current_timeFrame_Low = sys.maxsize

    # Iterate through all candles
    # to create candle for given TimeFrame
    for candle in candle_objects:
      current_time += 1
      current_timeFrame_High = max(candle.high, current_timeFrame_High)
      current_timeFrame_Low = min(candle.low, current_timeFrame_Low)
      if current_candle is None:
          current_candle = candle

      if current_time == timeFrame:
            current_candle.high = current_timeFrame_High
            current_candle.low = current_timeFrame_Low
            converted_candles.append(current_candle)
            current_time = 0
            current_candle = None
            current_timeFrame_High = -sys.maxsize
            current_timeFrame_Low = sys.maxsize

    # return the created candles
    return converted_candles


def process_csv_to_Candles(file):
    # create DataFrame using Pandas from uploaded file
    df = pd.read_csv(file)

    # Convert DataFrame rows into candle objects
    candle_objects = []
    for index, row in df.iterrows():
        candle_value = {
            'id': index,
            'date': row['DATE'],
            'open': row['OPEN'],
            'high': row['HIGH'],
            'low': row['LOW'],
            'close': row['CLOSE'],
        }
        candle = Candle(candle_value)
        candle_objects.append(candle)

    return candle_objects
    

    

def store_csv_file(uploaded_file):
    # create the path to store the uploaded files
    file_path = 'staticfiles/csv/'+uploaded_file.name

    # Save the uploaded file to the specified path
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    return file_path

def upload_csv(request):
    try:
        download_link = None
        if request.method == "POST":
            if request.FILES.get('csvFile'):
                uploadedFile = request.FILES['csvFile']
                timeFrame = request.POST.get('timeFrame')

                #save the csv file to staticfiles/csv directory using store_csv_file()
                stored_file_path = store_csv_file(uploadedFile)
            
                # Convert CSV into Candles
                candle_objects = process_csv_to_Candles(stored_file_path, )

                # Convert candle objects into given TimeFrame
                convertedCandles =  Candles_to_TimeFrame(candle_objects, int(timeFrame))

                # Convert TimeFrame Candles into JSON File
                converted_jsonfile = convert_to_json(convertedCandles,Path(stored_file_path).stem, timeFrame)

                # Provide the link to download the JSON file and pass it to render
                download_link = f'{converted_jsonfile}'
            
        return render(request, 'upload_csv.html', context={'download_link':download_link})
    except:
        return render(request, 'error.html')
