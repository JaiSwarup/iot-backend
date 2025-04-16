import os
import joblib
import pandas as pd
import thingspeak
import json
import asyncio

from datetime import datetime
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "*",
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data = {
  'C12B273': {
    'name': 'Sonu',
    'backlog': 100,
    'overtime': 100,
    'credits': 100,
    'idle': 20,
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
  
  def predict(self, id : str, data):
    data = {
      'wip': [data[id]['backlog']],  
      'over_time': [data[id]['overtime']],
      "incentive": [data[id]['credits']],
      "idle_time": [data[id]['idle']]
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
    ch = thingspeak.Channel(2735560)
    feed_data = json.loads(ch.get('feeds'))
    user_data = [item for item in feed_data['feeds'] if item['field1'] == id]
    return {
      "profile" : data[id],
      "entries": [{'timestamp': item['created_at'], 'value': item['field4']} for item in user_data],
      "prediction": productivity.predict(id, data).tolist()[0]
    }
  except Exception as e: 
    return e.__str__()

@app.post("/predict")
def predict_productivity(id: str):
  """
  Predicting an employee's productivity
  """
  try: 
    
    return {
        "id": id,
        "name": data[id]['name'],
        'prediction' : productivity.predict(id, data).tolist()[0]
    }
  except Exception as e:
    return e.__str__()
  
@app.get('/things')
def get_things():
  try:
    return get_feed_data()
  except Exception as e:
    return e

def get_feed_data():
  ch = thingspeak.Channel(2735560)
  return json.loads(ch.get('feeds'))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
      feed_data = get_feed_data()
      results = {}
      for feed in feed_data['feeds']:
        field1 = feed.get('field1')
        field2 = feed.get('field2')
        field3 = feed.get('field3')
        field4 = feed.get('field4')
        if field1 and field4:
          results[field2] = {'status': "IN" if field4 == "IN" else "OUT"}
      
      await websocket.send_json(results)
      await asyncio.sleep(15)