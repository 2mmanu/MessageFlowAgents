#!/bin/bash

usage() {
  echo "Usage: $0 [create|delete]"
  exit 1
}

if [[ $# -eq 0 || $1 == "create" ]]; then

    kubectl create namespace redis
    
    helm upgrade --install -n redis \
        redis oci://registry-1.docker.io/bitnamicharts/redis

    echo "password: kubectl get secret --namespace redis redis -o jsonpath="{.data.redis-password}" | base64 -d"
    echo "kubectl port-forward --namespace redis svc/redis-master 6379:6379"
    
elif [[ $1 == "delete" ]]; then

    helm delete -n redis redis

    kubectl delete namespace redis

else
  usage
fi