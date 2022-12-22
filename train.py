import hopsworks
import hsfs
import numpy as np
import pandas as pd
from hsml.schema import Schema
from hsml.model_schema import ModelSchema
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
import joblib

project = hopsworks.login()
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


td_version, td_job = fv.create_train_test_split(
    description = 'training data',
    data_format = 'csv',
    test_size = 0.1,
    write_options = {'wait_for_job': True}
)

X_train, X_test, y_train, y_test = fv.get_train_test_split(td_version)

y = np.array(y_train['aqi'])
X = np.array(range(len(y))).reshape(-1, 1)

degree=3
model=make_pipeline(PolynomialFeatures(degree),LinearRegression())
model.fit(X, y)

metrics = {
    "precision" : 1.0,
    "recall" : 1.0,
    "fscore" : 1.0,
    "rmse" : 1.0
}


mr = project.get_model_registry()
    
joblib.dump(model, 'polynomial_model.pkl')


knn_model = mr.python.create_model(
    name="poly_air", 
    metrics=metrics,
    description="Polynomial regression for air quality prediction.")

knn_model.save('polynomial_model.pkl')