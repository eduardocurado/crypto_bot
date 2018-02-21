from datetime import datetime


def convert_unix(date):
    utc_time = datetime.strptime((date + 'T00:27:31.807Z'), "%Y-%m-%dT%H:%M:%S.%fZ")
    return(utc_time - datetime(1970, 1, 1)).total_seconds()
