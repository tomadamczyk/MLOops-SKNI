import hopsworks
import requests
import json
import pandas as pd
import great_expectations as ge
import os

city = 'warsaw'
token = os.environ.get('AQI_TOKEN')

response = requests.get('https://api.waqi.info/feed/{}/?token={}'.format(city, token))
response = json.loads(response.content)['data']
data = {'aqi': float(response['aqi']),
        'pm25': float(response['iaqi']['pm25']['v']),
        'pm10': float(response['iaqi']['pm10']['v']),
        'no2': float(response['iaqi']['no2']['v']),
        'co': float(response['iaqi']['co']['v']),
        'time': str(response['time']['s'])}

print(data)

df = pd.DataFrame.from_records([data])
expectation_suite = ge.core.ExpectationSuite(expectation_suite_name="airquality")

expectation_suite.add_expectation(
  ge.core.ExpectationConfiguration(
  expectation_type="expect_column_values_to_be_between",
  kwargs={"column":"pm25", "min_value": 0, "max_value": 300}) 
)

project = hopsworks.login()

fs = project.get_feature_store()
air_fg = fs.get_or_create_feature_group(name="airquality",
        description="Air air quality observations",
        online_enabled=True,
        version=6,
        expectation_suite=expectation_suite,
        statistics_config={"enabled": True, "histograms": True, "correlations": True},
        event_time="time")

air_fg.insert(df)
