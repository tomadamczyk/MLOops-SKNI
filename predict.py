import hopsworks
import hsfs
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
import plotly.express as px

project = hopsworks.login()
fs = project.get_feature_store()
mr = project.get_model_registry()
model = mr.get_models("poly_air")[-1]
model_dir = model.download()
model = joblib.load(model_dir + "/polynomial_model.pkl")


air_fg = fs.get_feature_group("airquality", version=6)
query = air_fg.select(['aqi', 'co', 'no2', 'pm10', 'pm25', 'time'])
try: 
	fv = fs.get_feature_view("airwarsaw", version=2)
except:	
	fv = fs.create_feature_view(name='airwarsaw', 
	                            description='airquality',
	                            version=2,
	                            labels=['aqi', 'co', 'no2', 'pm10', 'pm25', 'time'],
	                            query=query)

td_version, td_job = fv.create_train_test_split(
    description = 'training data',
    data_format = 'csv',
    test_size = 0.1,
    write_options = {'wait_for_job': True}
)

X_train, X_test, y_train, y_test = fv.get_train_test_split(td_version)

y = np.array(y_train['aqi'])
X = np.array(range(len(y))).reshape(-1, 1)
prediction = model.predict(np.array(range(len(y), len(y)+12)).reshape(-1,1))
print(prediction)

fig = px.scatter()
fig.add_scatter(x=np.array(range(0, len(y))), y=np.array(y_train['aqi']), name='AQI values from the past.')
fig.add_scatter(x=np.array(range(len(y), len(y)+12)), y=prediction, name='AQI prediction for the next 12 hours')

fig.write_image(file='aqi.png', format="png", width=1920, height=1280)
