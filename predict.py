import hopsworks
import hsfs
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression

project = hopsworks.login()
fs = project.get_feature_store()
mr = project.get_model_registry()
model = mr.get_model("poly_air")
model_dir = model.download()
model = joblib.load(model_dir + "/polynomial_model.pkl")


fs = project.get_feature_store()
air_fg = fs.get_feature_group("airquality", version=6)
query = air_fg.select(['aqi', 'co', 'no2', 'pm10', 'pm25', 'time'])
try: 
	fv = fs.get_feature_view("airwarsaw", version=2)
except:	
	fv = fs.create_feature_view(name='airwarsaw', 
	                            description="airquality",
	                            version=2,
	                            labels=['aqi', 'co', 'no2', 'pm10', 'pm25', 'time'],
	                            query=query)
X_train, X_test, y_train, y_test = fv.get_train_test_split(5)

y = np.array(y_train['aqi'])
X = np.array(range(len(y))).reshape(-1, 1)

prediction = model.predict(np.array(range(len(y), len(y)+5)).reshape(-1,1))
print(prediction)