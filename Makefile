# Define variables for the image name and tag

# Image names
IMAGE_API         := prediction_api
IMAGE_MONITOR     := monitor_dashboard

# Container names
CONTAINER_API     := prediction_api_0803
CONTAINER_MONITOR := monitor_dashboard_0803

# Shared network & volume
NETWORK           := app-network
VOLUME            := logs-volume

# Paths
API_DIR           := Prediction_FastAPI
MONITOR_DIR       := Monitor_Streamlit

.PHONY: all init-volume build run clean evaluate

all: build

init-volume:
	@echo ">> Initializing volume '$(VOLUME)' with existing logs..."
	@docker volume inspect $(VOLUME) >/dev/null 2>&1 || docker volume create $(VOLUME)
	@docker run --rm \
	    -v $(VOLUME):/data \
	    -v $(shell pwd)/$(API_DIR)/logs:/src-logs \
	    alpine \
	    sh -c "cp /src-logs/prediction_logs.json /data/ || true"
	@echo ">> Volume initialized."


build: build-api build-monitor

build-api:
	@echo "Building Docker image: $(IMAGE_API)"
	docker build -t $(IMAGE_API) ./$(API_DIR)

build-monitor:
	@echo "Building Docker image: $(IMAGE_MONITOR)"
	docker build -t $(IMAGE_MONITOR) ./$(MONITOR_DIR)

# build: build-api build-monitor

run: build
	# Create network and volume if they don't exist
	@echo "Prepare network and volume..."
	docker network inspect $(NETWORK) >/dev/null 2>&1 || docker network create $(NETWORK)
# 	docker volume inspect $(VOLUME)   >/dev/null 2>&1 || docker volume create $(VOLUME)

	# FastAPI service
	@echo "Running FastAPI Docker container..."
	docker rm -f $(CONTAINER_API) >/dev/null 2>&1 || true
	docker run -d \
	  --name $(CONTAINER_API) \
	  --network $(NETWORK) \
	  -p 8000:8000 \
	  -v $(shell pwd)/$(API_DIR):/app \
	  -v $(VOLUME):/app/logs \
	  $(IMAGE_API)

	# Streamlit monitoring dashboard
	@echo "Running Streamlit Docker container..."
	docker rm -f $(CONTAINER_MONITOR) >/dev/null 2>&1 || true
	docker run -d \
	  --name $(CONTAINER_MONITOR) \
	  --network $(NETWORK) \
	  -p 8501:8501 \
	  -v $(shell pwd)/$(MONITOR_DIR):/app \
	  -v $(VOLUME):/app/logs \
	  $(IMAGE_MONITOR)

	@echo "Services are up:"
	@echo " • FastAPI at http://localhost:8000"
	@echo " • Streamlit Monitor at http://localhost:8501"

evaluate:
	python3 ./evaluate.py

clean:
	@echo "Removing Docker image: $(CONTAINER_API) $(CONTAINER_MONITOR)"

	docker rm -f $(CONTAINER_API) $(CONTAINER_MONITOR) || true
	docker network rm $(NETWORK)
	docker volume rm $(VOLUME)
	docker rmi $(IMAGE_API) $(IMAGE_MONITOR) || true

# http://127.0.0.1:8000
# http://127.0.0.1:8000/docs
# -v $(VOLUME):/app/logs \
# -v $(shell pwd)/$(API_DIR)/logs:/app/logs \
# -v $(shell pwd)/$(API_DIR)/logs/prediction_logs.json:/app/prediction_logs.json \