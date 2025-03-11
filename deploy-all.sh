set -e


echo "[INFO]: build msvc-integrator-service image"
if ! docker images | grep msvc-integrator-service
then
  docker build -t us-central1-docker.pkg.dev/uniandes-apps-no-monoliticas/misw4406-neoliticas-image-repo/msvc-integrator-service:latest ./msvc-integrator-service
  docker push us-central1-docker.pkg.dev/uniandes-apps-no-monoliticas/misw4406-neoliticas-image-repo/msvc-integrator-service:latest
#  minikube image load msvc-integrator-service:latest
fi


echo "[INFO]: build msvc-medical-record image"
if ! docker images | grep msvc-medical-record
then
  docker build -t us-central1-docker.pkg.dev/uniandes-apps-no-monoliticas/misw4406-neoliticas-image-repo/msvc-medical-record:latest ./msvc-medical-record
  docker push us-central1-docker.pkg.dev/uniandes-apps-no-monoliticas/misw4406-neoliticas-image-repo/msvc-medical-record:latest
#  minikube image load msvc-medical-record:latest
fi


echo "[INFO]: build msvc-auth image"
if ! docker images | grep msvc-auth
then
  docker build -t us-central1-docker.pkg.dev/uniandes-apps-no-monoliticas/misw4406-neoliticas-image-repo/msvc-auth:latest ./msvc-auth
  docker push us-central1-docker.pkg.dev/uniandes-apps-no-monoliticas/misw4406-neoliticas-image-repo/msvc-auth:latest
#  minikube image load msvc-auth:latest
fi



#eval "$(minikube -p minikube docker-env)"

echo "[INFO]: deploy all"
kubectl apply -f rabbitmq/k8s/

kubectl apply -f postgres/k8s/

kubectl apply -f msvc-integrator-service/k8s/
kubectl apply -f msvc-medical-record/k8s/
kubectl apply -f msvc-auth/k8s/


if ! kubectl get namespace logging > /dev/null 2>&1
then
  kubectl create namespace logging
fi

kubectl apply -f elastic/k8s/
