set -e

echo "[INFO]: build integrator service image"
if ! docker images | grep msvc-integrator-service
then
  docker build -t msvc-integrator-service:latest ./msvc-integrator-service
  minikube image load msvc-integrator-service:latest
fi

echo "[INFO]: build medical record image"
if ! docker images | grep msvc-medical-record
then
  docker build -t msvc-medical-record:latest ./msvc-medical-record
  minikube image load msvc-medical-record:latest
fi

eval "$(minikube -p minikube docker-env)"

echo "[INFO]: deploy all"
kubectl apply -f rabbitmq/k8s/

kubectl apply -f postgres/k8s/

kubectl apply -f msvc-integrator-service/k8s/

kubectl apply -f msvc-medical-record/k8s/
