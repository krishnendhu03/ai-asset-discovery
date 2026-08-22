import joblib

model = joblib.load("customer_model.joblib")

prediction = model.predict([[25, 50000, 2]])

print(prediction)