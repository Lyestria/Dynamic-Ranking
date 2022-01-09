import pandas as pd
import numpy as np
from datetime import date, timedelta
import os
import json

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

iso_code = {}
continent = {}
df = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv', parse_dates=['date'])
categories = df.columns[4:]

# Get the list of locations
locations = set()
for loc, cont, iso in zip(df['location'], df['continent'], df['iso_code']):
    if not loc in locations:
        locations.add(loc)
        iso_code[loc] = iso
        continent[loc] = cont

# Write iso and continent data
with open(os.path.join('data', 'metadata.json'), 'w') as outfile:
    json.dump({'continent':continent, 'iso_code':iso_code}, outfile)

# Get the date range
min_date = df['date'].min()
max_date = df['date'].max()

# Create data frames for the categoriess
data = [[date] + [np.nan for loc in locations] for date in daterange(min_date, max_date + timedelta(1))]
default_frame = pd.DataFrame(data, columns=['date'] + list(locations))
frames = {category:default_frame.copy() for category in categories}

# Fill in the data according to the tables
for ind, row in df.iterrows():
    for category in categories:
        loc = row['location']
        date = row['date']
        frames[category][loc, date] = row[category]
        
# Output rows to tables
for category, frame in frames.items():
    path = os.path.join('data', f'{category}.csv')
    frame.to_csv(path, index=False)
