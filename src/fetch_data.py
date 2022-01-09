import pandas as pd
import numpy as np
from datetime import date, timedelta
import os
import json
import logging

logging.basicConfig(level=logging.INFO)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

iso_code = {}
continent = {}
df = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv', parse_dates=['date'])
categories = df.columns[4:]

# Get the list of locations
logging.info('Extracting location data')
locations = set()
for loc, cont, iso in zip(df['location'], df['continent'], df['iso_code']):
    if not loc in locations:
        locations.add(loc)
        iso_code[loc] = iso
        continent[loc] = cont

# Write iso and continent data
with open(os.path.join('data', 'location_data.json'), 'w') as outfile:
    json.dump({'continent':continent, 'iso_code':iso_code}, outfile)

# Pivot to table with data type
for category in categories:
    logging.info(f'Extracting data for {category}')
    frame = df.pivot(index='date', columns='location', values=category)
    path = os.path.join('data', f'{category}.csv')
    frame.to_csv(path)
