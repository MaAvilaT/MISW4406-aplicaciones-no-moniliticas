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
#minikube ssh
#docker images

./deploy-all.sh
```

You must configure a DB instance, and define a file (probably called `config.yaml`)
like the following one at the directory `postgres/k8s`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
stringData:
  username: '?'
  password: '?'
  database: '?'
  host: '?'
  port: '?'

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
data:
  POSTGRES_SSL_MODE: 'require'
  POSTGRES_CONNECTION_TIMEOUT: '30'
  POSTGRES_POOL_SIZE: '10'
```

This works for local development, if you wish to deploy to real env, you need to
define the artifact registry repo for the docker images, push them, and create a svc
account in GCP or your cloud provider to grant access to the pods in your cluster
to the images.

### Sending a test message

Use the postman collection.





















