# Model Monitoring

## Introduction

A multi-container application where two services run independently but communicate with each other:

A lightweight **FastAPI**-based service that classifies text as **Positive** or **Negative**, and provides sentiment probabilities.

A **Streamlit App** that reads the logs from the shared volume to visualize model performance.

A **Docker** Volume that persist log data and share it between the two containers.

### **Project Architecture**

- `Monitor_Streamlit`: contains files to build streamlit

- `Prediction_FastAPI`: contains files to build FastAPI

- `Makefile`: builds multi-containers for this application

- `evaluate.py` and `test.json`: sends the default reviews to FastAPI and evaluate the entire process.

---

## Prerequisites

To run this app, please make sure `Docker`, `Git`, `FastAPI`, `Postman`, and other essential python packages mentioned in the `requirements.txt` are installed. 

Turn on **Docker Desktop** at step 1.

---

## Features & Endpoints

Test the follow command in the Postman

### **1. `GET /health`**
- **Purpose**: Health check to ensure the API is running.
- **Response**: `{ "status": "ok" }`

### **2. `POST /predict`**
- **Purpose**: Classify input text as Positive or Negative.
* **Running Example**: http://127.0.0.1:8000/predict?text=This%20movie%20was%20a%20masterpiece!&true_sentiment=Positive.
- **Request Body**:
  ```json
  {
    "text": "I love this!",
    "true_sentiment":"Positive"
  }
  ```
* **Successful Response**:

  ```json
  {
    "sentiment": "Positive"
  }
  ```
* **Error Cases**:

  * `400 Bad Request` if the text is empty.
  * `503 Service Unavailable` if the model fails to load.

### **3. `POST /predict_proba`**

* **Purpose**: Returns sentiment along with the model’s confidence.
* **Running Example**: http://127.0.0.1:8000/predict_proba?text=This%20movie%20was%20a%20masterpiece!&true_sentiment=Positive.
* **Request Body**:

  ```json
  {
    "text": "I love this!",
    "true_sentiment":"Positive"
  }
  ```
* **Successful Response**:

  ```json
  {
    "sentiment": "Positive",
    "probability": "0.9532"
  }
  ```
* **Error Cases**:

  * `400 Bad Request` if the text is empty.
  * `503 Service Unavailable` if the model fails to load.

### **4. `GET /example`**

* **Purpose**: Returns a random review from the local IMDB dataset (`IMDB_Dataset.csv`).
* **Response**:

  ```json
  {
    "review": "This movie is fantastic—I loved every moment!"
  }
  ```

---

## How to run this app 

- Download the entire folder by `git clone git@github.com:jiansfoggy/4705_jiansun_assignment5.git`

- Enter the folder `cd 4705_jiansun_assignment5`

- Build and run the API locally using **Makefile**:

  1. **Install dependencies**

      In the `./4705_jiansun_assignment3`, Run `make build` to build the Docker image

      ```bash
      make build
      ```

  2. **Start the server**

      Run `make run` to process the container from the image

      ```bash
      make run
      ```

      Services are up:
      ```bash
      • FastAPI at http://localhost:8000
      • Streamlit Monitor at http://localhost:8501
      ```
  
  3. **Activate FastAPI**

      Run the following code to activate the localhost
      ```bash
      uvicorn main:app --reload
      ```

  4. **Delete Containers and Images**

      Run `make clean` to delete the created docker containers and images.

      ```bash
      make clean
      ```
  
  5. **Evaluate the APP with Default File**

      Run `make evaluate` to run `evaluate.py`, which reads the default review file `test.json`, loop through each item, send the review to the running FastAPI service's `/predict` endpoint, and print a final accuracy score.

      ```bash
      make evaluate
      ```

---

## Interactive Docs

Once running, FastAPI automatically generates its documentation. Explore and test all endpoints via Swagger UI at:

```
http://127.0.0.1:8000/docs
```

---

## Usage Example

```bash
# Check health
curl http://127.0.0.1:8000/health

# Predict sentiment
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"text":"What a lovely story!!","true_sentiment":"Positive"}' \
     http://127.0.0.1:8000/predict

# Predict with probability
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"text":"What a lovely story!","true_sentiment":"Positive"}' \
     http://127.0.0.1:8000/predict_proba

# Check example
curl http://127.0.0.1:8000/example
```

---

## Notes

* Ensure `sentiment_model.pkl` and `IMDB_Dataset.csv` are in the project subdirectory `Prediction_FastAPI` and `Monitor_Streamlit`.
* The `Makefile` automates setup, training, and running tasks.
* Produced docs `/docs` reflect real-time API schema and let you issue live requests.
