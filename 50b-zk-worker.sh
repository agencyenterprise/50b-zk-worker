#!/bin/sh
# SPDX-License-Identifier: Apache-2.0

if [ "$1" = "setup" ]; then
  echo "Setting up 50b ZK Worker..."

  echo "Installing Nitro Enclaves Cli..."
  amazon-linux-extras install aws-nitro-enclaves-cli -y
  yum install aws-nitro-enclaves-cli-devel -y

  echo "Setting up credentials..."
  usermod -aG ne ec2-user
  usermod -aG docker ec2-user

  echo "Starting Nitro Enclave and Docker services..."
  systemctl enable --now nitro-enclaves-allocator.service
  systemctl enable --now docker

  echo "Done setting up 50b ZK Worker."

  exit 0

elif [ "$1" = "start" ]; then
  if [ -z "$2" ]; then
    echo "Please provide a wallet address."
    echo "Usage: $0 start <wallet_address>"
    exit 1
  fi

  PUBLIC_PORT=5000
  ENCLAVE_CID=16

  if [ ! -z "$3" ]; then
    PUBLIC_PORT=$3
  fi

  if [ ! -z "$4" ]; then
    ENCLAVE_CID=$4
  fi

  HOST_IP=$(curl -s http://checkip.amazonaws.com | sed 's/\./-/g')
  WORKER_URL=http://ec2-$HOST_IP.compute-1.amazonaws.com:$PUBLIC_PORT
  HUB_URL=https://ddfa1056febf4955a6b3950472e6c937.api.mockbin.io

  echo "Starting 50b ZK Worker..."

  echo "Pulling Docker images..."
  docker pull aeandreborges/50b-zk-worker-public:latest
  docker pull aeandreborges/50b-zk-worker-secure:latest

  echo "Building Nitro Enclave image..."
  nitro-cli build-enclave --docker-uri aeandreborges/50b-zk-worker-secure:latest --output-file 50b-zk-worker-secure.eif

  echo "Starting 50 ZK Worker Secure enclave..."
  nitro-cli run-enclave --enclave-name 50b-zk-worker-secure-$ENCLAVE_CID --cpu-count 2 --memory 512 --enclave-cid $ENCLAVE_CID --eif-path 50b-zk-worker-secure.eif --debug-mode
  echo "Starting 50 ZK Worker Public container..."

  docker run --name 50b-zk-worker-public-$PUBLIC_PORT -p $PUBLIC_PORT:$PUBLIC_PORT -d -e WORKER_WALLET=$2 -e ENCLAVE_CID=$ENCLAVE_CID -e WORKER_URL=$WORKER_URL -e HUB_URL=$HUB_URL aeandreborges/50b-zk-worker-public:latest
  
  echo "Done starting 50b ZK Worker."

  exit 0

elif [ "$1" = "stop" ]; then
  echo "Stopping 50b ZK Worker..."
  
  PUBLIC_PORT=5000
  ENCLAVE_CID=16

  if [ ! -z "$2" ]; then
    PUBLIC_PORT=$2
  fi

  if [ ! -z "$3" ]; then
    ENCLAVE_CID=$3
  fi

  echo "Stopping and removing 50b ZK Worker Public container..."
  docker stop 50b-zk-worker-public-$PUBLIC_PORT
  docker rm 50b-zk-worker-public-$PUBLIC_PORT
  
  echo "Terminating 50b ZK Worker Secure enclave..."
  nitro-cli terminate-enclave --enclave-name 50b-zk-worker-secure-$ENCLAVE_CID

  echo "Done stopping 50b ZK Worker."

  exit 0

elif [ "$1" = "logs" ]; then
  nitro-cli console --enclave-name 50b-zk-worker-secure

  exit 0

else
    echo "Usage: $0 setup|start|stop|logs"

    exit 1
fi
