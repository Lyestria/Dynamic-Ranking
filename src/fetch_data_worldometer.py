from bs4 import BeautifulSoup
from collections import defaultdict
import requests
import re
import js2xml
import itertools
import os
import csv

project_root = os.path.dirname(os.path.dirname(__file__))
base_url = 'https://www.worldometers.info/coronavirus/'

def get_data(country, x_values, headers):
    """Takes the country name and grabs the data for that country for every single graph
    """
    # Find the charts that we want
    soup = BeautifulSoup(requests.get(f"{base_url}country/{country}").content, 'html.parser')
    scripts = soup.find_all('script', text=re.compile(r"Highcharts\.chart\('"))

    tables = {}
    for script in scripts:
        # Parse Javascript code into XML format and read the data
        parsed = js2xml.parse(script.text)
        table = parsed.xpath('//functioncall[./arguments/string]')[0]
        header = table.xpath('./arguments/string')[0].text
        headers.add(header)
        cur_x_values = table.xpath("(//property[@name='categories'])[1]//string/text()")
        if x_values == None:
            x_values = cur_x_values
        y_elements = table.xpath("(//property[@name='data'])[1]/array/*")
        y_values = ["0" if element.tag == 'null' else element.get('value') for element in y_elements]
        # Align everything by the last date (which should always match)
        tables[header] = ["NULL"] * (len(x_values)-len(y_values)) + y_values

    return tables, x_values

def get_countries():
    content = requests.get(base_url).content.decode("utf-8") 
    return list(set(re.findall(r'href="country\/([a-z\-]*)\/', content)))

def write_to_file(filepath, x_values, countries, data):
    parent = os.path.dirname(filepath)
    os.makedirs(parent, exist_ok=True)
    
    with open(filepath, 'w', newline='') as csvfile:
        print(f"Writing to file: {filepath}")
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['Countries'] + countries)
        for i in range(len(x_values)):
            writer.writerow([x_values[i]] + [row[i] for row in data])

def load_data():
    x_values = None
    headers = set()
    countries = get_countries()
    # Search China first to get all of the valid dates
    countries.remove('china')
    countries.insert(0, 'china')
    print(f"Found {len(countries)} countries")
    data = defaultdict(list)
    country_tables = {}
    for country in countries:
        print(f"Fetching data for {country}")
        tables, x_values = get_data(country, x_values, headers)
        country_tables[country] = tables
    for country, tables in country_tables.items():
        for header in headers:
            if header in tables:
                data[header].append(tables[header])
            else:
                data[header].append(["NULL"] * len(x_values))
    # Path to store scraped information
    for header, y_values in data.items():
        data_path = os.path.join(project_root, 'data', f'{header}.csv')
        write_to_file(data_path, x_values, countries, y_values)

if __name__ == "__main__":
    load_data()
