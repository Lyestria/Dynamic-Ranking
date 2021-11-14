from bs4 import BeautifulSoup
import requests
import re
import js2xml
import itertools
import os
import csv
import asyncio

project_root = os.path.dirname(os.path.dirname(__file__))
base_url = 'https://www.worldometers.info/coronavirus/'


def get_data(country, chart_type):
    """Takes the country name and returns a list of all the data points in the coronavirus-cases-linear graph for that country
    """
    # Find the chart that we want
    soup = BeautifulSoup(requests.get(base_url + "country/" + country).content, 'html.parser')
    chart = soup.find('script', text=re.compile(r"Highcharts\.chart\('{}'".format(chart_type)))

    # Parse Javascript code into XML format and read the data
    parsed = js2xml.parse(chart.text)
    data = [d.xpath(".//array/number/@value") for d in parsed.xpath("//property[@name='data']")]
    categories = parsed.xpath("//property[@name='categories']//string/text()")
    
    return categories, data[0]

def get_countries():
    """Finds the list of country names on Worldometer"""
    content = requests.get(base_url).content.decode("utf-8") 
    return list(set(re.findall(r'country\/([a-z\-]*)\/', content)))

def write_to_file(filepath, x_values, countries, data):
    parent = os.path.dirname(filepath)
    os.makedirs(parent)
    with open(file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['Countries'] + countries)
        for i in range(len(x_values)):
            writer.writerow([x_values[i]] + [row[i] for row in data])

def load_data(chart_type = 'coronavirus-cases-linear'):
    """Loads the data points for all available countries on Worldometer"""
    countries = get_countries()
    print(f"Found {len(countries)} countries")
    x_values = []
    y_values = []
    for country in countries:
        print(f"Fetching data for {country}")
        x_values, country_data = get_data(country, chart_type)
        y_values.append(country_data)
    write_to_file()
    # Path to store scraped information
    data_path = os.path.join(project_root, 'data', chart_type + '.csv')
    os.makedirs(data_path)
    data_file = os.path.join(data_path, chart_type)
    write_to_file(data_file, x_values, countries, y_values)
        
    return x_values, y_values
