docker login

docker build -t aeandreborges/50b-zk-worker-public ./public
docker build -t aeandreborges/50b-zk-worker-secure ./secure

docker push aeandreborges/50b-zk-worker-public
docker push aeandreborges/50b-zk-worker-secure