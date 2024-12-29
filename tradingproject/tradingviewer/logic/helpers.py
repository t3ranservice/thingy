from datetime import datetime

def shortfloat(data):
    return round(float(data), 2)

def convert_epoch(date):
    return int(datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp()) * 1000