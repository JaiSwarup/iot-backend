import os
import joblib
import numpy as np
import pandas as pd

from fastapi import FastAPI

app = FastAPI()

data = {
  'C12B273': {
    'name': 'Sonu',
    'backlog': 100,
    'overtime': 100,
    'credits': 100,
    'idle_time': 20,
  },
  '59BAAF2': {
    'name': 'Rahul',
    'backlog': 22,
    'overtime': 1,
    'credits': 400,
    'idle': 0,
  }
}

class ProductivityModel:
  """
  Predicting an employee's productivity
  """
  def __init__(self):
    self.model = joblib.load('models/rf_model.joblib')
    pass
  
  def predict(self, id : str):
    data = {
      'wip': data[id]['backlog'],
      'over_time': data[id]['overtime'],
      "incentive": data[id]['credits'],
      "idle_time": data[id]['idle']
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

@app.get("/users")
def get_users():
  """Get user data."""
  try: 
    return data
  except Exception as e: 
    return e.__str__()

@app.get("/users/{id}")
def get_user_data(id: str):
  """Get user data."""
  try: 
    return data[id]
  except Exception as e: 
    return e.__str__()

@app.post("/predict")
def predict_productivity(id: str):
  """
  Predicting an employee's productivity
  """
  try: 
    return productivity.predict(id).tolist()
  except Exception as e:
    return e.__str__()

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))