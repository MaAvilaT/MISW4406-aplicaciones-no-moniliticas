# MISW4406-aplicaciones-no-moniliticas


# Kubernetes (minikube) setup

This guide explains how to set up and test the RabbitMQ producer and consumer applications in Minikube.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Project Structure

Create the following directory structure:

        .
        ├── create-images.yml
        ├── deploy-all.yml
        ├── msvc-integrator-service
        │   ├── Dockerfile
        │   ├── requirements.txt
        │   └── src
        │       ├── app.py
        │       └── __init__.py
        ├── msvc-medical-record
        │   ├── Dockerfile
        │   ├── requirements.txt
        │   └── src
        │       ├── app.py
        │       └── __init__.py
        └── README.md

## Setup Steps

### 1. Start Minikube

```bash
minikube start
```

### 2. Enable the Minikube Docker environment

```bash
eval $(minikube docker-env)
```

This allows Minikube to use locally built Docker images.

### 3. Build the Docker images

```bash
# Build producer image
cd ./msvc-integrator-service
docker build -t msvc-integrator-service:latest .

# Build consumer image
cd ../msvc-medical-record
docker build -t msvc-medical-record:latest .
```

### 4. Deploy to Kubernetes

```bash
cd ..
kubectl apply -f deploy-all.yaml
```

### 5. Check deployment status

```bash
kubectl get pods
```

Wait until all pods show `Running` status.

## Testing the Application

### 1. Get service URLs

```bash
minikube service msvc-integrator-service --url
minikube service msvc-medical-record --url
```

Save these URLs for testing.

### 2. Send a test message to the producer

Using curl (replace with the actual producer URL):

```bash
curl -X POST \
  "$(minikube service msvc-integrator-service --url)/send" \
  -H 'Content-Type: application/json' \
  -d '{
    "message_id": "123",
    "content": "Test message",
    "timestamp": "2025-02-24T12:00:00Z",
    "priority": "high"
}'
```

### 3. Check received messages in the consumer

Using curl (replace with the actual consumer URL):

```bash
curl "$(minikube service msvc-medical-record --url)/messages"
```

You should see the message you sent via the producer.

### 4. Access RabbitMQ Management Interface

```bash
# Port forward RabbitMQ management console
kubectl port-forward service/rabbitmq 15672:15672
```

Open your browser and navigate to `http://localhost:15672/`
- Username: guest
- Password: guest

Here you can monitor queues, messages, and other RabbitMQ metrics.

### 5. Clean up

When you're done testing:

```bash
kubectl delete -f deploy-all.yml
minikube stop
```

## Advanced Tests

### Send multiple messages

```bash
for i in {1..5}; do
  curl -X POST \
    http://$(minikube service producer --url)/send \
    -H 'Content-Type: application/json' \
    -d "{
      \"message_id\": \"$i\",
      \"content\": \"Test message $i\",
      \"timestamp\": \"2025-02-24T12:00:00Z\",
      \"priority\": \"medium\"
    }"
  echo ""
done
```

### Clear message history

```bash
curl -X POST http://$(minikube service consumer --url)/clear
```
