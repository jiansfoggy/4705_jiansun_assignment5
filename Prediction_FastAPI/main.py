import joblib, json, os, time
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(
    title="Sentiment Analysis API",
)

os.makedirs("./logs", exist_ok=True)

try:
    model = joblib.load('./sentiment_model.pkl')
    print("Model loaded successfully.")
except FileNotFoundError:
    print("Error: Model file 'diabetes_model.joblib' not found.")
    print("Please run the 'train.py' script first to generate the model file.")
    model = None

class TextInput(BaseModel):
    text: str = Field(..., example="I loved this movie!")
    true_sentiment: str = Field(..., example="Positive")
    # text: str
    # true_sentiment: str

@app.get("/health")
def health():
    """
    Health Check Endpoint
    This endpoint is used to verify that the API server is running and responsive.
    It's a common practice for monitoring services.
    """
    return {"status": "ok"}

@app.post("/predict")
async def predict(input_data: TextInput):
    """
    Prediction Endpoint
    Takes a feature vector and returns a binary prediction (0 or 1).
    """
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. Cannot make predictions."
        )
    
    text = input_data.text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
            )
   
    category = ["Negative","Positive"]
    prediction = model.predict([text])[0]
    pred = category[int(prediction)]

    data = {
    "timestamp": time.time(),
    "request_text": text,
    "predicted_sentiment": pred,
    "true_sentiment": input_data.true_sentiment
    }

    with open("./logs/prediction_logs.json", "a", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")
    
    return {"sentiment": pred}

@app.post("/predict_proba")
def predict_probability(input_data: TextInput):
    """
    Prediction with Probability Endpoint
    Takes a feature vector and returns the prediction along with the
    probabilities for each class (0 and 1).
    """
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. Cannot make predictions."
        )

    text = input_data.text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
            )
        
    category = ["Negative","Positive"]
    prediction = model.predict([text])[0]
    pred_proba = model.predict_proba([text])
    pred = category[int(prediction)]
    prob = pred_proba[0][int(prediction)]

    return {
        "sentiment": pred,
        "probability": f"{prob:.4f}"
    }

@app.get("/example")
def example():
    """
    Health Check Endpoint
    This endpoint is used to verify that the API server is running and responsive.
    It's a common practice for monitoring services.
    """
    df = pd.read_csv("./IMDB_Dataset.csv")
    X = df.review
    random_review = X.sample().iloc[0]
    return {"review": random_review}

# uvicorn main:app --reload
# curl 'http://127.0.0.1:8000/health'
# POST http://localhost:8000/predict?text=This%20movie%20was%20a%20masterpiece!&true_sentiment=Positive