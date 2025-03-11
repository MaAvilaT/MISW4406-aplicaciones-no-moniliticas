# minikube env

docker image rm -f msvc-integrator-service
docker image rm -f msvc-medical-record
docker image rm -f msvc-auth
docker image prune -a -f



eval "$(minikube -p minikube docker-env)"

echo "[INFO]: undeploy all"
#kubectl delete -f rabbitmq/k8s/

kubectl delete -f postgres/k8s/

kubectl delete -f msvc-integrator-service/k8s/
kubectl delete -f msvc-medical-record/k8s/
kubectl delete -f msvc-auth/k8s/

sleep 4

docker image rm -f msvc-integrator-service
docker image rm -f msvc-medical-record
docker image rm -f msvc-auth

docker image prune -a -f

docker container prune -f
minikube cache delete
#kubectl delete all --all
docker volume prune -f
