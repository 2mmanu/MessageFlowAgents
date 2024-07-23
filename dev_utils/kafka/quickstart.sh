#!/bin/bash

usage() {
  echo "Usage: $0 [create|delete]"
  exit 1
}

if [[ $# -eq 0 || $1 == "create" ]]; then

    kubectl create namespace confluent
    kubectl config set-context --current --namespace confluent

    helm repo add confluentinc https://packages.confluent.io/helm
    helm repo update
    helm upgrade --install \
        confluent-operator confluentinc/confluent-for-kubernetes

    # kubectl apply -f ./quota.yaml
    kubectl apply -f ./confluent-platform.yaml
    kubectl apply -f ./topics.yaml 

    echo "kubectl port-forward controlcenter-0 9021:9021"
    echo "http://localhost:9021/clusters"
    echo "kubectl port-forward svc/kafka 9092:9092"
    
elif [[ $1 == "delete" ]]; then

    kubectl delete -f ./confluent-platform.yaml

    helm delete confluent-operator

    kubectl delete namespace confluent

else
  usage
fi