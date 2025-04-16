import os
import joblib
import numpy as np
import pandas as pd

from fastapi import FastAPI

app = FastAPI()

class ProductivityModel:
  """
  Predicting an employee's productivity
  """
  def __init__(self):
    self.model = joblib.load('models/rf_model.joblib')
    pass
  
  def predict(self, id : int):
    data = {
      'wip': [100],
      'over_time': [100],
      "incentive": [100],
      "idle_time": [1]
    }
    return self.model.predict(pd.DataFrame(data))

productivity = ProductivityModel()

@app.get("/")
def hello_world():
  """Example Hello World route."""
  try: 
    name = os.environ.get("NAME", "World")
    return f"Hello {name}!"
  except Exception as e: 
    return e.__str__()

@app.post("/predict")
def predict_productivity(id: int):
  """
  Predicting an employee's productivity
  """
  try: 
    return productivity.predict(id).tolist()
  except Exception as e:
    return e.__str__()

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))