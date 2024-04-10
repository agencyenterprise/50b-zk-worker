PORT=5000
if [ ! -z "$1" ]; then
    PORT=$1
fi

HUB_URL=http://localhost:3000
if [ ! -z "$2" ]; then
    HUB_URL=$2
fi

WORKER_WALLET=0x80963163d664fD34fc2e15104904CBba213377b3
if [ ! -z "$2" ]; then
    WORKER_WALLET=$2
fi

export MODE=Mocked
export WORKER_WALLET=$WORKER_WALLET
export WORKER_URL=http://localhost:$PORT
export HUB_URL=$HUB_URL

export FLASK_APP=worker-public.py

flask run --host 0.0.0.0 --port $PORT
